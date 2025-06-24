from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse  #Resposta em JSON/HTML
from sqlalchemy.orm import Session
from db.connection import SessionLocal, engine #importação da base de dados
from models.acesso import Utilizadores, RegistoAcesso, AcessosNegados, Permissoes, Base #Tabelas da base de dados
from datetime import datetime   #TEMPO
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc     #Utilizado para ordenar os dados no html

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="web"), name="static")   #cria o diretório estático para o html (web)
global estado_atual     # Variável global para o estado da porta
estado_atual = "verde"  # Estado inicial 
ID_Armario = 10         #Armário 10

#Acesso à base de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Endpoint onde apenas recebe o UID do cartão RFID
@app.post("/acessos")
async def verificar_acesso(rfid_uid: str = Body(...),db: Session = Depends(get_db)):
    global estado_atual
    print(f"UID recebido: '{rfid_uid}'")    #UID do cartão lido


    #casos não  autorizados
    def registar_acesso_negado(uid: str):
        db.add(AcessosNegados(
            UID_Rejeitado=uid,
            Abertura=datetime.utcnow(),
            Fecho=None,
            ID_Armario=ID_Armario
        ))
        db.commit()
        return JSONResponse(content={"acesso": 0}, status_code=200)
    
    if rfid_uid == "TEMPO_EXPIRADO": #>10s
        
        estado_atual = "amarelo"
        return registar_acesso_negado("SEM_CARTAO")

    utilizador = db.query(Utilizadores).filter_by(UID=rfid_uid).first() #está na tabela de utilizadores?
    if not utilizador:
        estado_atual = "amarelo"
        return registar_acesso_negado(rfid_uid)

    permissao = db.query(Permissoes).filter_by(ID_Armario=ID_Armario, UID=rfid_uid).first() #tem permissão para abrir o armário em questão?
    if not permissao:
        estado_atual = "amarelo"
        return registar_acesso_negado(rfid_uid)
    

    #por exclusão de partes, se não houver erro, o acesso é permitido
    db.add(RegistoAcesso(
        UID=rfid_uid,
        Abertura=datetime.utcnow(),
        Fecho=None,
        ID_Armario=ID_Armario
    ))
    db.commit()
    return JSONResponse(content={"acesso": 1}, status_code=200)


#De acordo com o tipo de acesso, o sistema vai registar o fecho da porta
@app.post("/estado-porta")
async def verificar_acesso(estado: str = Body(...),db: Session = Depends(get_db)):
    global estado_atual
    print(f"Estado recebido: '{estado}'") #enviado pelo ESP32
        # fecho_permitido ->verde
        # fecho_negado ->vermelho
        # aberta_a_espera -> castanho
        # aberto_autorizado -> verde_claro
        # aberto_não_autorizado -> amarelo
    
    def registar_fecho_negado():
        ultimo_registo = db.query(AcessosNegados).order_by(AcessosNegados.Contador.desc()).first() #funcao para obter o último registo->contador mais alto
        if ultimo_registo:
            ultimo_registo.Fecho = datetime.utcnow()
            db.commit()
            return JSONResponse(content={"mensagem": "Fecho registado"})
        else:
            return JSONResponse(content={"mensagem": "Erro ao registar fecho"})
    
    def registar_fecho_permitido():
        ultimo_registo = db.query(RegistoAcesso).order_by(RegistoAcesso.Contador.desc()).first()
        if ultimo_registo:
            ultimo_registo.Fecho = datetime.utcnow()
            db.commit()
            return JSONResponse(content={"mensagem": "Fecho registado"})
        else:
            return JSONResponse(content={"mensagem": "Erro ao registar fecho"})

    if estado == "fecho_negado":
        estado_atual = "vermelho"
        return registar_fecho_negado()

    elif estado == "fecho_permitido":
        estado_atual = "verde"
        return  registar_fecho_permitido()
    
    elif estado == "aberto_a_espera":
        estado_atual = "castanho"
        return JSONResponse(content={"mensagem": "Porta aberta ,à espera do cartão"})
    
    elif estado == "aberto_não_autorizado":
        estado_atual = "amarelo"
        return JSONResponse(content={"mensagem": "Porta aberta ,sem autorização"})

    elif estado == "aberto_autorizado":
        estado_atual = "verde_claro"
        return JSONResponse(content={"mensagem": "Acesso autorizado - porta aberta"})
    else:
        return JSONResponse(content={"mensagem": "Estado desconhecido"}, status_code=400)
    
#Endpoint para obter o estado atual da porta
@app.get("/estado")
def estado():
    return {"cor": estado_atual, "id_armario": ID_Armario}

@app.get("/", response_class=HTMLResponse)
def interface_web():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    

#Histórico dos 10 acessos mais recentes
@app.get("/historico")
def ultimos_acessos(db: Session = Depends(get_db)):

    #consulta na tabela de acessos permitidos
    acessos_permitidos = (   
        db.query(RegistoAcesso)
        .order_by(desc(RegistoAcesso.Abertura))
        .limit(10)
        .all()
    )
    #conulta na tabela de acessos negados
    acessos_negados = (
        db.query(AcessosNegados)
        .order_by(desc(AcessosNegados.Abertura))
        .limit(10)
        .all()
    )
    acessos = []  #Junta as informações das duas tabelas
    #formato correto
    for a in acessos_permitidos:
        acessos.append({
            "uid": a.UID,
            "abertura": a.Abertura,
            "fecho": a.Fecho,
            "tipo": "permitido"
        })
    for a in acessos_negados:
        acessos.append({
            "uid": a.UID_Rejeitado,
            "abertura": a.Abertura,
            "fecho": a.Fecho,
            "tipo": "negado"
        })
    

    acessos.sort(key=lambda x: x["abertura"], reverse=True)  #ordena os acessos pela abertura
    ultimos_10 = acessos[:10]   #10 acessos mais recentes
    for a in ultimos_10:
        a["abertura"] = a["abertura"].strftime("%Y-%m-%d %H:%M:%S")
        a["fecho"] = a["fecho"].strftime("%Y-%m-%d %H:%M:%S") if a["fecho"] else "—"
    
    return {"acessos": ultimos_10} 