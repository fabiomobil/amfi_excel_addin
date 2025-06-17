ADD-IN AMFI - CALCULADORA DE DEBENTURES v1.0
============================================

DESCRIÇÃO:
Add-in Excel para cálculos financeiros de debêntures com índice de subordinação.
Desenvolvido para facilitar análises de estrutura de capital em operações de debênture.

INSTALAÇÃO:
1. Execute "Instalar-AMFI.bat" como Administrador
   OU
   Execute "Instalar-AMFI.ps1" no PowerShell
2. Abra o Excel
3. Vá em: Arquivo > Opções > Suplementos
4. Em "Gerenciar" selecione "Suplementos do Excel" e clique "Ir..."
5. Marque "AMFI" na lista e clique OK

FUNÇÃO PRINCIPAL:
=AmfiCalc(Senior; Junior; IndiceSubordinacao; "OPERACAO")

PARÂMETROS:
- Senior: Valor da série Senior (em reais)
- Junior: Valor da série Junior/Subordinada (em reais)
- IndiceSubordinacao: Índice mínimo de subordinação (decimal: 0.2 = 20%)
- Operacao: Tipo de cálculo desejado (ver abaixo)

OPERAÇÕES DISPONÍVEIS:
- "FALTA" ou "F"       = Quanto falta adicionar na Junior para enquadrar o IS
- "DISPONIVEL" ou "D"  = Quanto está disponível na Senior com a garantia atual
- "VALIDAR" ou "V"     = Se o IS está sendo respeitado (1=sim, 0=não)
- "IS_ATUAL" ou "A"    = Calcular o IS atual da estrutura

EXEMPLOS PRÁTICOS:

Cenário: Senior = R$ 800.000, Junior = R$ 150.000, IS mínimo = 20%

1. Verificar se está enquadrado:
   =AmfiCalc(800000; 150000; 0,2; "VALIDAR")
   Resultado: 0 (não está enquadrado)

2. Quanto falta na Junior:
   =AmfiCalc(800000; 150000; 0,2; "FALTA")
   Resultado: 50.000 (precisa adicionar R$ 50.000 na Junior)

3. Quanto pode liberar na Senior:
   =AmfiCalc(800000; 150000; 0,2; "DISPONIVEL")
   Resultado: 0 (não pode liberar nada, está desenquadrado)

4. IS atual:
   =AmfiCalc(800000; 150000; 0,2; "IS_ATUAL")
   Resultado: 0,1579 (15,79% - abaixo do mínimo de 20%)

CONCEITOS IMPORTANTES:

Índice de Subordinação (IS):
- Mede o nível de proteção da série Senior
- IS = (Junior + Mezanino) / (Senior + Junior + Mezanino)
- Exemplo: IS = 20% significa que 20% do PL serve como garantia

Fórmulas utilizadas:
- Junior necessária = (IS × Senior) ÷ (1 - IS)
- Senior máximo = Junior × (1 - IS) ÷ IS

REQUISITOS TÉCNICOS:
- Microsoft Excel 2010 ou superior
- Windows 7 ou superior
- Permissões para instalar add-ins

SOLUÇÃO DE PROBLEMAS:

Erro "Arquivo não encontrado":
- Certifique-se de que AMFI.xlam está na mesma pasta do instalador

Função não aparece no Excel:
- Verifique se o add-in está ativado em Arquivo > Opções > Suplementos

Erro #VALOR! na função:
- Verifique se os parâmetros estão corretos
- IS deve ser entre 0 e 1 (ex: 0,2 para 20%)
- Valores não podem ser negativos

DESINSTALAÇÃO:
Execute "Desinstalar-AMFI.bat"

SUPORTE:
Para dúvidas técnicas ou melhorias, contate o desenvolvedor.

HISTÓRICO DE VERSÕES:
v1.0 - Versão inicial
- Função AmfiCalc com 4 operações principais
- Instalador automático
- Validação de parâmetros
- Funções auxiliares opcionais

========================================
© 2025 - ADD-IN AMFI
Calculadora de Debêntures