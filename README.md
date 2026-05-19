# Sistema de Monitorização e Controlo de Acessos a Armários de Telecomunicações

Projeto desenvolvido no âmbito da unidade curricular de **PESTA** da Licenciatura em Engenharia Eletrotécnica e de Computadores do **ISEP**.

O objetivo principal deste projeto é a criação de um sistema inteligente de monitorização e controlo de acessos para armários exteriores da Porto Digital, permitindo supervisão remota, controlo de acessos e recolha de informação em tempo real.

---

# Contexto

A crescente necessidade de monitorização remota de infraestruturas urbanas levou ao desenvolvimento de soluções capazes de:

- Monitorizar acessos físicos;
- Garantir maior segurança operacional;
- Centralizar informação num sistema acessível remotamente;
- Reduzir intervenção manual;
- Melhorar rastreabilidade e auditoria de eventos.

Este projeto pretende responder a essas necessidades através da integração de hardware com uma webapp

---

# Funcionalidades

## Controlo de Acessos

- Gestão de acessos aos armários;
- Registo de eventos de abertura e fecho;
- Identificação de utilizadores/autorização;
- Histórico de acessos.

## Monitorização Remota

- Consulta do estado dos armários em tempo real;
- Deteção de eventos e alterações de estado;
- Comunicação com os dispositivos.

## Sistema de Captura de Imagem

- Integração com ESP32-CAM;
- Captura de imagens associadas aos eventos;
- Validação visual remota.

## API Backend

- Gestão centralizada dos dados;
- Comunicação entre dispositivos e plataforma;
- Persistência de dados;
- Endpoints preparados para expansão futura.

---

# Arquitetura do Sistema

```text
┌────────────────────┐
│    ESP32 / CAM     │
│  Sensores e I/O    │
└─────────┬──────────┘
          │
          │ Comunicação
          ▼
┌────────────────────┐
│    API Backend     │
│  Gestão de Dados   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Base de Dados      │
│ Eventos e Registos │
└────────────────────┘
```

---

# Estrutura do Repositório

```bash
Pesta_Isep/
│
├── PoeCamera_esp32/      # Código relacionado com ESP32-CAM
├── armarios-api/         # Backend/API do sistema
├── Tabelas_bd.txt     # Estrutura da base de dados
├── README.md
└── .vscode/              # Configurações do ambiente de desenvolvimento
```

---

# Tecnologias Utilizadas

## Backend

- Python
- API REST

## Frontend / Interface

- HTML

## Sistemas Embebidos

- ESP32
- ESP32-CAM
- C++


Adicionar futuramente:

- Capturas de ecrã;
- Diagramas elétricos;
- Fluxogramas;
- Fotografias do protótipo;
- Vídeos de demonstração.

---


# Autor

## Gustavo Marques

Estudante de Engenharia Eletrotécnica e de Computadores no ISEP.

GitHub:
https://github.com/Gustavo176176/Pesta_Isep

---

# Licença

Este projeto foi desenvolvido para fins académicos no contexto da unidade curricular de PESTA do ISEP.
