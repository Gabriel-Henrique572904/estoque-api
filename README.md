# Estoque API

Backend em Python para controle de estoque de pequenos comércios, desenvolvido para o **Checkpoint 1 — Arquitetura, Backend e Regras de Negócio**.

A aplicação permite cadastrar categorias e produtos, registrar entradas e saídas de mercadorias e consultar o saldo e o histórico de movimentações. Os dados são persistidos em SQLite e a API possui documentação interativa Swagger/OpenAPI.

## Integrantes

| Nome | RM |
| --- | --- |
| Gabriel Henrique Rodrigues Ochsendorf | 572904 |
| Guilherme Araujo Pinto | 568963 |
| Francisco | 574165 |

## Problema, público-alvo e solução

Pequenos comércios que controlam mercadorias por anotações ou planilhas atualizadas manualmente podem perder o acompanhamento das entradas, das saídas e do saldo disponível. Isso dificulta a conferência do estoque e permite registrar saídas incompatíveis com a quantidade existente.

O público-alvo são proprietários e funcionários de pequenos estabelecimentos que precisam organizar produtos e acompanhar suas movimentações.

O objetivo principal é centralizar os registros em uma API, mantendo o saldo vinculado às movimentações e impedindo saídas superiores à quantidade disponível. A primeira versão concentra-se no backend; o Swagger permite demonstrar e testar suas operações.

## Funcionalidades e escopo do CP1

- Cadastro, listagem, consulta individual, atualização e exclusão de categorias.
- Cadastro, listagem, consulta individual, atualização e exclusão de produtos.
- Filtro de produtos por categoria.
- Registro de entradas e saídas com atualização do saldo.
- Consulta do histórico geral ou das movimentações de um produto.
- Consulta individual de movimentações.
- Validação dos dados recebidos e tratamento de conflitos de negócio.
- Persistência em banco relacional e documentação Swagger/OpenAPI.

Interface visual própria, autenticação, fornecedores, pedidos de venda e relatórios avançados ficam fora do escopo desta versão.

## Regras de negócio

| Código | Regra |
| --- | --- |
| RN01 | Toda categoria deve possuir nome preenchido, com até 100 caracteres, e esse nome deve ser único. |
| RN02 | Todo produto deve pertencer a uma categoria existente. |
| RN03 | O SKU identifica o produto de forma única. Espaços nas extremidades são removidos e as letras são convertidas para maiúsculas. O limite é de 40 caracteres. |
| RN04 | O nome do produto é obrigatório e possui limite de 120 caracteres. A descrição é opcional, com até 500 caracteres. |
| RN05 | O preço não pode ser negativo. São aceitos até oito dígitos na parte inteira e duas casas decimais. |
| RN06 | Todo produto é cadastrado com estoque zero. |
| RN07 | O cadastro e a atualização de produtos não aceitam o campo `estoque`. O saldo é alterado pelas movimentações. |
| RN08 | Uma movimentação deve referenciar um produto existente e possuir tipo `ENTRADA` ou `SAIDA`. |
| RN09 | A quantidade de uma movimentação deve ser um número inteiro maior que zero. |
| RN10 | Uma entrada soma unidades ao saldo; uma saída subtrai unidades. |
| RN11 | Uma saída superior ao saldo disponível é recusada com HTTP 409. A tentativa recusada não altera o saldo nem gera registro no histórico. |
| RN12 | A atualização do saldo e o registro da movimentação são realizados na mesma transação. Em caso de falha durante essa operação, as alterações são desfeitas. |
| RN13 | Categorias com produtos vinculados não podem ser excluídas. |
| RN14 | Produtos com movimentações registradas não podem ser excluídos, preservando seu histórico. |
| RN15 | Movimentações podem ser criadas e consultadas. Não existem rotas para editar ou excluir esses registros. Ajustes devem ser registrados como novas movimentações, com uma observação que explique a correção. |
| RN16 | A data e a hora da movimentação são geradas pelo banco em UTC. A observação é opcional, com até 500 caracteres. |

Os campos de texto têm os espaços nas extremidades removidos. Na versão atual, nomes de categorias diferenciam maiúsculas de minúsculas: `Informática` e `informática` são valores distintos. Campos adicionais não previstos nos schemas são recusados.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
| --- | --- |
| Python 3.11 | Linguagem utilizada no desenvolvimento. Ambiente demonstrado: Python 3.11.9. |
| FastAPI | Implementação dos endpoints REST e geração da documentação OpenAPI. |
| Uvicorn | Servidor para executar a aplicação FastAPI. |
| SQLAlchemy 2 | Mapeamento das entidades, consultas e transações com o banco. |
| SQLite | Persistência local em um arquivo de banco de dados. |
| Pydantic | Validação dos dados de entrada e estruturação das respostas. |
| pydantic-settings | Leitura das configurações pelo ambiente e pelo arquivo `.env`. |
| Swagger UI | Documentação interativa e execução manual das requisições. |
| Git e GitHub | Versionamento e disponibilização do código-fonte. |
| VS Code | Editor utilizado no desenvolvimento. |

As versões das dependências estão registradas em `requirements.txt`.

## Arquitetura e organização

| Arquivo ou pasta | Responsabilidade |
| --- | --- |
| `app/main.py` | Cria a aplicação, registra as rotas e inicializa as tabelas ausentes. |
| `app/config.py` | Carrega a configuração do banco. |
| `app/database.py` | Define o engine, a base dos modelos e as sessões do banco; ativa as chaves estrangeiras do SQLite. |
| `app/models.py` | Define as tabelas, os relacionamentos e as restrições de integridade. |
| `app/schemas.py` | Define os contratos de entrada e saída e as validações dos dados. |
| `app/routers/categorias.py` | Define os endpoints de categorias. |
| `app/routers/produtos.py` | Define os endpoints de produtos. |
| `app/routers/movimentacoes.py` | Define os endpoints de movimentações. |
| `app/services/categorias.py` | Executa as operações e regras de categorias. |
| `app/services/produtos.py` | Executa as operações e regras de produtos. |
| `app/services/movimentacoes.py` | Controla as entradas, as saídas e a consistência entre saldo e histórico. |
| `requirements.txt` | Registra as dependências necessárias para executar o projeto. |
| `.env.example` | Modelo de configuração para outros ambientes. |
| `.gitignore` | Exclui do versionamento o ambiente virtual, as configurações locais e os arquivos gerados. |

As rotas recebem as requisições e utilizam os schemas para validar os dados. Os serviços executam as regras de negócio e usam os modelos e as sessões do SQLAlchemy para acessar o banco. Cada requisição que depende do banco recebe uma sessão, fechada ao final de seu uso.

Na saída de estoque, a condição de saldo suficiente faz parte do próprio comando de atualização no banco. O saldo é decrementado com base no valor armazenado, evitando a sobrescrita de um saldo calculado a partir de uma leitura anterior.

## Banco de dados e entidades

O banco padrão é o arquivo `estoque.db`, criado automaticamente quando a aplicação é iniciada. O SQLite dispensa a instalação de um servidor de banco separado.

| Entidade | Campos principais | Relacionamento |
| --- | --- | --- |
| Categoria | `id`, `nome` | Uma categoria pode ter zero ou vários produtos. |
| Produto | `id`, `sku`, `nome`, `descricao`, `preco`, `estoque`, `categoria_id` | Cada produto pertence a uma categoria e pode ter zero ou várias movimentações. |
| Movimentacao | `id`, `produto_id`, `tipo`, `quantidade`, `observacao`, `data_hora` | Cada movimentação pertence a um produto. |

`categoria_id` e `produto_id` são chaves estrangeiras. O banco aplica restrições de unicidade, integridade referencial e verificações para preço e estoque não negativos, quantidade positiva e tipos válidos de movimentação.

A criação automática usa `Base.metadata.create_all`. Esse recurso cria tabelas ausentes, mas não executa migrações de tabelas já existentes. Os dados permanecem salvos quando o servidor é reiniciado.

## Instalação e execução

### Preparação

Instale Python 3.11 e obtenha os arquivos deste repositório, por clone ou por **Code → Download ZIP** no GitHub. Abra um terminal na pasta que contém `app` e `requirements.txt`.

Todos os comandos a seguir devem ser executados nessa pasta principal do projeto.

### macOS e Linux

Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Na primeira configuração, crie o arquivo local a partir do modelo:

```bash
cp .env.example .env
```

Inicie a API:

```bash
python -m uvicorn app.main:app --reload
```

### Windows — PowerShell

Os comandos abaixo utilizam diretamente o Python do ambiente virtual:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Acessos

Após aparecer `Application startup complete`, acesse:

- [Status da API](http://127.0.0.1:8000/)
- [Swagger UI](http://127.0.0.1:8000/docs)
- [Especificação OpenAPI em JSON](http://127.0.0.1:8000/openapi.json)

Esses endereços são locais: o professor ou outro integrante deve executar o projeto em seu próprio computador para acessá-los. O terminal precisa permanecer com o servidor em execução. Para encerrá-lo, pressione `Control + C` no terminal.

### Variáveis de ambiente

O arquivo `.env` deve conter:

```dotenv
DATABASE_URL=sqlite:///./estoque.db
```

| Variável | Finalidade |
| --- | --- |
| `DATABASE_URL` | Define a conexão SQLite. O exemplo utiliza `estoque.db` na pasta a partir da qual o servidor foi iniciado. |

Sem essa variável, `app/config.py` utiliza como padrão um caminho absoluto para `estoque.db` na pasta principal do projeto. A configuração de conexão desta versão foi preparada para SQLite.

O `.env` e o banco local são ignorados pelo Git. O `.env.example` deve ser versionado. Em uma instalação nova, as tabelas são criadas vazias; os cadastros podem ser feitos pelo Swagger.

## Endpoints

| Método | Endpoint | Operação | Sucesso |
| --- | --- | --- | --- |
| GET | `/` | Verificar o funcionamento da API. | 200 |
| POST | `/categorias` | Criar uma categoria. | 201 |
| GET | `/categorias` | Listar categorias. | 200 |
| GET | `/categorias/{categoria_id}` | Consultar uma categoria. | 200 |
| PUT | `/categorias/{categoria_id}` | Atualizar o nome da categoria. | 200 |
| DELETE | `/categorias/{categoria_id}` | Excluir uma categoria sem produtos. | 204 |
| POST | `/produtos` | Criar um produto com estoque zero. | 201 |
| GET | `/produtos` | Listar produtos, com filtro opcional de categoria. | 200 |
| GET | `/produtos/{produto_id}` | Consultar um produto e seu saldo. | 200 |
| PUT | `/produtos/{produto_id}` | Substituir os dados cadastrais do produto. | 200 |
| DELETE | `/produtos/{produto_id}` | Excluir um produto sem movimentações. | 204 |
| POST | `/movimentacoes` | Registrar entrada ou saída. | 201 |
| GET | `/movimentacoes` | Listar movimentações, com filtro opcional de produto. | 200 |
| GET | `/movimentacoes/{movimentacao_id}` | Consultar uma movimentação. | 200 |

As listagens aceitam `offset` (padrão 0, mínimo 0) e `limite` (padrão 100, entre 1 e 100). Produtos também aceitam `categoria_id`; movimentações aceitam `produto_id`. As movimentações são listadas do maior para o menor ID.

O `PUT` de produto exige SKU, nome, preço e categoria. A descrição é opcional e, quando omitida, passa a ser nula. O saldo não é alterado pelo `PUT`.

### Respostas e erros

Respostas de cadastro, consulta individual e atualização contêm um objeto JSON. Listagens retornam uma lista JSON. Exclusões bem-sucedidas retornam HTTP 204 sem corpo.

| Código | Significado |
| --- | --- |
| 200 | Consulta ou atualização concluída. |
| 201 | Recurso criado. |
| 204 | Exclusão concluída, sem corpo de resposta. |
| 404 | Recurso ou relacionamento necessário não encontrado. |
| 409 | Conflito de negócio, como saldo insuficiente, duplicidade ou exclusão de um registro com vínculos. |
| 422 | Dados ou parâmetros inválidos, conforme os schemas. |
| 500 | Falha interna; o serviço de criação de movimentações trata erros do SQLAlchemy com rollback e uma mensagem genérica. |

Exemplo de conflito de negócio:

```json
{
  "detail": "Estoque insuficiente para realizar a saída."
}
```

Erros de validação utilizam a estrutura padrão do FastAPI, com uma lista em `detail` indicando os campos inválidos. Valores monetários são representados como strings decimais nas respostas, por exemplo `"34.90"`.

## Roteiro de demonstração

No Swagger, abra a operação, clique em **Try it out**, preencha os parâmetros e o JSON e clique em **Execute**. Confira o resultado em **Server response**; a seção de exemplos da documentação não representa uma requisição executada.

### 1. Criar categoria

Em `POST /categorias`:

```json
{
  "nome": "Informática"
}
```

Anote o ID retornado. Os exemplos seguintes consideram categoria e produto com ID 1; se os IDs recebidos forem diferentes, substitua-os nos respectivos campos.

### 2. Criar produto

Em `POST /produtos`:

```json
{
  "sku": "PROD-001",
  "nome": "Mouse USB",
  "descricao": "Mouse com conexão USB",
  "preco": "29.90",
  "categoria_id": 1
}
```

O produto deve ser criado com estoque zero. Se a categoria ou o SKU já estiverem cadastrados, utilize os registros existentes ou valores novos para a demonstração.

### 3. Registrar entrada

Em `POST /movimentacoes`:

```json
{
  "produto_id": 1,
  "tipo": "ENTRADA",
  "quantidade": 10,
  "observacao": "Entrada inicial de mercadorias"
}
```

Execute uma vez. Para um produto inicialmente zerado, o saldo passa a 10.

### 4. Registrar saída

Em `POST /movimentacoes`:

```json
{
  "produto_id": 1,
  "tipo": "SAIDA",
  "quantidade": 3,
  "observacao": "Venda de 3 unidades"
}
```

Execute uma vez. Consulte `GET /produtos/1`: o saldo esperado nessa sequência é 7.

### 5. Demonstrar a regra de saldo insuficiente

Tente registrar uma saída de 10 unidades para o mesmo produto, que agora possui 7. O resultado esperado é HTTP 409. Consulte o produto e o histórico: o saldo deve continuar em 7, com somente as duas movimentações válidas.

### 6. Demonstrar atualização, exclusão e persistência

- Atualize o preço para `"34.90"` em `PUT /produtos/{produto_id}`, enviando os demais campos obrigatórios. O estoque deve permanecer em 7.
- Crie um produto temporário com SKU diferente, sem registrar movimentações. Exclua esse produto pelo ID recebido: o resultado esperado é HTTP 204.
- Reinicie o servidor e consulte o produto utilizado nas movimentações. Seus dados e saldo devem permanecer salvos.

Cada `POST /movimentacoes` bem-sucedido registra uma nova operação. Reexecutar uma entrada ou saída altera novamente o saldo.

## Validação manual realizada

Os seguintes cenários foram executados pelo Swagger durante o desenvolvimento:

| Cenário | Resultado observado |
| --- | --- |
| Criar e listar a categoria Informática | HTTP 201 no cadastro e 200 na listagem. |
| Criar o produto Mouse USB | HTTP 201 e estoque inicial zero. |
| Registrar entrada de 10 unidades | HTTP 201 e saldo consultado igual a 10. |
| Registrar saída de 3 unidades | HTTP 201 e saldo consultado igual a 7. |
| Tentar retirar 10 unidades com saldo 7 | HTTP 409 com mensagem de estoque insuficiente. |
| Reiniciar e consultar o produto | HTTP 200 e saldo preservado em 7. |
| Consultar o histórico | HTTP 200 com entrada de 10 e saída de 3, sem registro da tentativa recusada. |
| Atualizar o preço do Mouse USB | HTTP 200, preço 34.90 e estoque mantido em 7. |
| Criar e excluir produto temporário | HTTP 201 no cadastro e 204 na exclusão. |

## Organização do trabalho

O acompanhamento será organizado em um quadro Kanban no Trello, com as listas **A fazer**, **Em andamento**, **Em revisão** e **Concluído**. As tarefas devem identificar o responsável, o objetivo e o critério de conclusão. O quadro deve refletir o trabalho efetivamente realizado pelo grupo.

As frentes de trabalho incluem definição do problema e das regras, arquitetura, banco de dados, categorias, produtos, movimentações, validação da API, documentação, versionamento e preparação da apresentação.

## Links do projeto

| Recurso | Endereço |
| --- | --- |
| Repositório GitHub | [Estoque API no GitHub](https://github.com/Gabriel-Henrique572904/estoque-api) |
| Quadro Trello | [Estoque API — Checkpoint 1](https://trello.com/b/ONvTBjr3/estoque-api-checkpoint-1) |
| Swagger local | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| OpenAPI local | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) |

Os links pendentes devem ser preenchidos antes da entrega do checkpoint.
