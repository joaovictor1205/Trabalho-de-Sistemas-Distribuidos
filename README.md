# Trabalho-de-Sistemas-Distribuidos


                                  Trabalho de Sistemas Distribuídos – Entrega 0
                                          João Victor da Costa Gonçalves
                                                  11711BCC050


    • Introdução

      O NerdRoom é uma aplicação multiplataforma para encontro de Empresas e Desenvolvedores que desejam diminuir a formalidade na busca de vagas e novos funcionários.

    • Funcionamento

      Quando um usuário novo acessa o sistema ele deve efetuar o Cadastro e selecionar se sua ocupação é como Recrutador de uma empresa ou Funcionário.
      Caso ele selecione a opção Recrutador, sua conta passará a receber informações de Funcionários e ele poderá selecionar funcionários para um possível agendamento de entrevistas.
      Caso ele selecione a opção Funcionário, sua conta passará a receber informações de Empresas e ele poderá visualizar as vagas ofertadas pelos Recrutadores, caso considere apto para tal vaga, ele poderá selecioná-la.
      De início nenhuma opção de chat entre Recrutador e Funcionário é permitida, pois o chat só é inicializado caso o Recrutador selecione o Funcionário, e caso o Funcionário também selecione o Recrutador.
      A seleção de um Funcionário para com o Recrutador, ou vice-versa é chamada de “Like”, caso ambos deem Like entre si e o chat é inicializado, ocorrendo o “Match”.
      Os Matchs podem ser desfeitos caso o Funcionário não deseje mais tal vaga, ou caso o Recrutador não queira mais prosseguir com o processo seletivo.

    • Arquitetura do Software

      • Aplicação (WebSocket)
          ◦ Comunicação TCP/IP
      • Servidor (Express/Node.js)
      • Json (Arquivo para armazenamento do histórico do chat e das informações de Registro)
      
    • Lista de Testes

      • Testes de Caixa-Preta (Testes Funcionais)
          ◦ Verificar se o sistema atende todos os Requisitos Funcionais
          ◦ Verificar duplicações de Funcionários ou Empresas
          ◦ Buscar por Funcionários ou Empresas inexistentes
      • Teste de Concorrência
          ◦ Verificar se o sistema atende múltiplos usuários sem haver falhas
      • Teste de Recuperação de Falhas
          ◦ Verificar se o sistema volta ao último estado com sucesso antes de ocorrer a falha
      • Teste de Carga
          ◦ Verificar se o sistema permanece em alta performance mesmo com vários clientes acessando ao mesmo tempo
          
    • Histórias de Usuário

        ◦ US001 – Login
            ▪ Como usuário do sistema eu desejo fazer login para acessar as telas e utilizar o TinderIn
              
        ◦ US002 – Cadastro de Funcionário
            ▪ Como um Funcionário em busca de uma oportunidade de emprego desejo realizar meu cadastro no TinderIn
              
        ◦ US003 – Cadastro de Recrutador
            ▪ Como um Recrutador em busca de novos Funcionários para minha empresa desejo realizar meu cadastro no TinderIn
              
        ◦ US004 – Match
            ▪ Como um Funcionário/Recrutador desejo utilizar a funcionalidade de Like para abrir o chat
              
        ◦ US005 – Cancelar Match
            ▪ Como um Funcionário/Recrutador desejo cancelar o meu Like e não permitir mais que o chat esteja disponível
              
        ◦ US006 – Chat
            ▪ Como um Funcionário/Recrutador desejo utilizar o chat para me comunicar com outra pessoas
