# 🟡 Pac-Man em Python

```text
╔══════════════════════════════════════════════════════════╗
║           COMUNIDADE SAMUEL MAGGI // PYTHON            ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║        • • • • • • • • • • • • • • • •              ║
║        • ┌─────┐ • ┌─────────┐ • ┌─────┐ •            ║
║        • │     │ • │         │ • │     │ •            ║
║        • └─────┘ • └────┐    │ • └─────┘ •            ║
║        • • • • • • •   │ 👻 │ • • • • • •            ║
║                         │    │                          ║
║                  🟡  • • • •  👻                       ║
║                         │    │                          ║
║        • • • • • • • • • • • • • • • •              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

Projeto educacional inspirado no clássico **Pac-Man**, desenvolvido em **Python + Pygame** para a **Comunidade Samuel Maggi**.

O projeto demonstra como construir um jogo completo utilizando movimentação em grid, colisões, lógica de inimigos, pontuação, níveis, partículas, persistência de dados e efeitos sonoros gerados pelo próprio Python.

---

## ✨ Funcionalidades

- 🟡 Personagem com animação da boca
- 👻 Quatro fantasmas
- 🧠 Comportamentos diferentes para cada fantasma
- 🧱 Labirinto completo
- ⚪ Pontos espalhados pelo mapa
- ✨ Power Pellets
- 👻 Fantasmas vulneráveis durante o Power-Up
- 🍒 Fruta bônus
- 💥 Sistema de partículas
- ❤️ Sistema de vidas
- 🏆 Pontuação
- 📈 High Score
- 💾 Recorde salvo em JSON
- 🎚️ Sistema de níveis
- ⏸️ Pause
- 🔊 Controle de áudio
- 🎵 Efeitos sonoros gerados pelo próprio código
- ☠️ Game Over
- 🔁 Reinício da partida

---

## 🎮 Controles

| Tecla | Ação |
|---|---|
| ⬆️ ⬇️ ⬅️ ➡️ | Movimentar |
| W A S D | Movimentar |
| Espaço | Iniciar |
| P | Pausar |
| M | Ligar ou desligar o som |
| R | Reiniciar após Game Over |

---

## 🔊 Áudio gerado pelo próprio Python

Um dos diferenciais deste projeto é que os efeitos sonoros são sintetizados pelo próprio código.

O jogo não precisa de arquivos MP3 ou WAV externos para os principais efeitos.

O Python cria os sinais sonoros e o mixer do Pygame reproduz esses efeitos durante a partida.

Existem sons para:

- início da partida
- coleta de pontos
- power pellet
- captura de fantasmas
- fruta bônus
- perda de vida
- passagem de nível
- game over
- pause

---

## 🧠 Inteligência dos fantasmas

Os quatro fantasmas possuem comportamentos diferentes:

```text
CHASER
Persegue diretamente a posição do jogador.

AMBUSHER
Tenta prever para onde o Pac-Man está indo.

TRICKSTER
Combina perseguição com movimentos imprevisíveis.

COWARD
Altera o comportamento dependendo da distância do jogador.
```

Isso permite estudar princípios básicos de comportamento de NPCs em jogos.

---

## 🧱 Como o mapa funciona

O labirinto é definido através de uma matriz de caracteres.

Exemplo:

```python
MAPA = [
    "#####################",
    "#o.......#.......o..#",
    "#.###.##.#.##.###...#",
]
```

Cada caractere representa um elemento do jogo:

```text
# = parede
. = ponto
o = power pellet
P = jogador
G = fantasma
```

O código percorre essa matriz e transforma cada posição nos elementos gráficos exibidos pelo Pygame.

---

## 🛠️ Tecnologias utilizadas

- Python 3
- Pygame
- JSON
- Math
- Random
- Pathlib

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/samuelcmaggi/pacman-python-pygame.git
```

### 2. Entre na pasta

```bash
cd pacman-python-pygame
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o jogo

```bash
python pacman.py
```

No Windows, usando o Python Launcher:

```powershell
py -3.13 pacman.py
```

---

## 📚 Conceitos praticados

Este projeto utiliza diversos fundamentos importantes de programação:

- variáveis
- listas
- dicionários
- funções
- classes
- orientação a objetos
- loops
- condicionais
- eventos
- colisões
- vetores
- movimentação em grid
- máquina de estados
- lógica de NPCs
- partículas
- geração de áudio
- persistência com JSON
- renderização em tempo real

---

## 📂 Estrutura do projeto

```text
pacman-python-pygame/
│
├── pacman.py
├── README.md
├── requirements.txt
└── .gitignore
```

O recorde é salvo localmente no arquivo:

```text
comunidade_samuel_maggi_highscore.json
```

Esse arquivo é criado automaticamente durante o jogo e não é enviado ao GitHub.

---

## ⚠️ Projeto educacional

Este projeto foi criado para fins de estudo e demonstração de programação com Python e Pygame.

Pac-Man é uma marca associada aos seus respectivos detentores de direitos.

Este projeto não possui afiliação oficial com os criadores ou proprietários da marca.

---

## 👨‍💻 Autor

### Samuel Maggi

Criador da **Comunidade Samuel Maggi**.

Conteúdos sobre Python, programação, desenvolvimento, tecnologia e projetos práticos.

---

## ⭐ Curtiu o projeto?

Se este projeto te ajudou a aprender algo novo, considere deixar uma **estrela no repositório**. ⭐

E continue acompanhando os próximos projetos da Comunidade Samuel Maggi.
