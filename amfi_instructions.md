INSTRUÇÕES DE INSTALAÇÃO DETALHADAS - ADD-IN AMFI
================================================

🎯 OBJETIVO:
Instalar o add-in AMFI para usar a função AmfiCalc() no Excel

📁 ANTES DE COMEÇAR:

1. EXTRAIA TODOS OS ARQUIVOS para uma pasta local
   Exemplo: C:\AMFI\ ou Desktop\AMFI\

2. CERTIFIQUE-SE de que a pasta contenha TODOS estes arquivos:
   ✓ AMFI.xlam                    (arquivo principal do add-in)
   ✓ Instalar-AMFI.bat          (instalador simples)
   ✓ Desinstalar-AMFI.bat       (desinstalador)
   ✓ Instalar-AMFI.ps1          (instalador PowerShell)
   ✓ LEIA-ME.txt                (manual do usuário)
   ✓ INSTRUCOES-INSTALACAO.txt  (este arquivo)

📂 ESTRUTURA CORRETA:
C:\AMFI\
├── AMFI.xlam                    ← OBRIGATÓRIO: arquivo do add-in
├── Instalar-AMFI.bat          ← Execute este para instalar
├── Desinstalar-AMFI.bat       
├── Instalar-AMFI.ps1          
├── LEIA-ME.txt                
└── INSTRUCOES-INSTALACAO.txt  

🚀 COMO INSTALAR:

OPÇÃO 1 - Instalador Batch (Recomendado):
1. Navegue até a pasta onde estão TODOS os arquivos
2. Clique com botão direito em "Instalar-AMFI.bat"
3. Selecione "Executar como administrador"
4. Aguarde a mensagem "INSTALACAO CONCLUIDA COM SUCESSO!"
5. Pressione qualquer tecla para fechar

OPÇÃO 2 - Instalador PowerShell (Mais robusto):
1. Abra PowerShell como administrador
2. Navegue até a pasta: cd "C:\AMFI"
3. Execute: .\Instalar-AMFI.ps1
4. Aguarde a conclusão

⚙️ ATIVAR NO EXCEL:

Após a instalação:
1. Abra o Microsoft Excel
2. Vá em: Arquivo > Opções
3. Clique em "Suplementos" (menu esquerdo)
4. Na parte inferior, em "Gerenciar", selecione "Suplementos do Excel"
5. Clique no botão "Ir..."
6. Na janela que abrir, marque a caixa "AMFI"
7. Clique "OK"

✅ TESTE DE FUNCIONAMENTO:

Em qualquer célula do Excel, digite:
=AmfiCalc(800000; 150000; 0,2; "FALTA")

Se retornar o número 50000, a instalação foi bem-sucedida! 🎉

❌ ERROS COMUNS E SOLUÇÕES:

ERRO: "Arquivo AMFI.xlam não encontrado"
SOLUÇÃO: 
- Verifique se o AMFI.xlam está na MESMA PASTA do .bat
- NÃO execute o .bat de outra pasta
- NÃO copie apenas o .bat para desktop

ERRO: Função não aparece no Excel
SOLUÇÃO:
- Verifique se seguiu os passos de ativação no Excel
- Feche e reabra o Excel
- Verifique se não há erro de digitação na função

ERRO: #VALOR! na função
SOLUÇÃO:
- Verifique os parâmetros:
  - Senior e Junior devem ser números positivos
  - IndiceSubordinacao deve ser entre 0 e 1 (ex: 0,2 para 20%)
  - Operacao deve ser "FALTA", "DISPONIVEL", "VALIDAR" ou "IS_ATUAL"

ERRO: "Falha ao copiar o arquivo"
SOLUÇÃO:
- Execute como administrador
- Feche o Excel antes de instalar
- Verifique se não há antivírus bloqueando

🗑️ DESINSTALAR:

Para remover completamente o add-in:
1. Execute "Desinstalar-AMFI.bat" como administrador
2. OU delete manualmente: %APPDATA%\Microsoft\AddIns\AMFI.xlam

📞 PRECISA DE AJUDA?

Se ainda tiver problemas:
1. Verifique se seguiu TODOS os passos na ordem
2. Certifique-se de que tem permissões de administrador
3. Tente fechar completamente o Excel e repetir a instalação
4. Verifique se o Windows não bloqueou os arquivos (propriedades > desbloquear)

🎯 DICA PARA ADMINISTRADORES DE TI:

Para instalar em múltiplas máquinas:
1. Copie a pasta AMFI completa para um compartilhamento de rede
2. Execute via script: \\servidor\compartilhado\AMFI\Instalar-AMFI.ps1 -Silent
3. O parâmetro -Silent suprime as mensagens interativas

===============================================
Qualquer dúvida, consulte o arquivo LEIA-ME.txt
===============================================