"""
Calculus Handler - Cálculos financeiros para IS (Índice de Subordinação)
"""

def _calcular_jr_por_is(pl, is_percentual):
    """
    Calcula JR baseado no PL e IS desejado.
    
    Args:
        pl (float): Patrimônio Líquido
        is_percentual (float): Índice de Subordinação em percentual (ex: 20 para 20%)
    
    Returns:
        float: Valor de JR
    """
    is_decimal = is_percentual / 100
    jr = pl * is_decimal
    return jr


def _calcular_sr_por_jr_pl(pl, jr):
    """
    Calcula SR baseado no PL e JR.
    
    Args:
        pl (float): Patrimônio Líquido
        jr (float): Juros Remuneratórios
    
    Returns:
        float: Valor de SR
    """
    sr = pl - jr
    return sr


def _calcular_is_atual(pl, jr):
    """
    Calcula o IS atual baseado no PL e JR.
    IS = JR / PL
    
    Args:
        pl (float): Patrimônio Líquido
        jr (float): Juros Remuneratórios
    
    Returns:
        float: IS em percentual
    """
    if pl == 0:
        return 0
    is_percentual = (jr / pl) * 100
    return is_percentual


def _calcular_adicional_para_is_desejado(pl_inicial, is_atual_decimal, is_desejado_decimal):
    """
    Calcula quanto precisa adicionar ao JR para atingir o IS desejado.
    Resolve a equação: (JR + x) / (PL + x) = IS_desejado
    
    Args:
        pl_inicial (float): Patrimônio Líquido inicial
        is_atual_decimal (float): IS atual em decimal (ex: 0.15 para 15%)
        is_desejado_decimal (float): IS desejado em decimal (ex: 0.20 para 20%)
    
    Returns:
        dict: Contém todos os valores calculados
    """
    # Converte decimais para percentuais para usar a função existente
    is_atual_percentual = is_atual_decimal * 100
    is_desejado_percentual = is_desejado_decimal * 100
    
    # Calcula JR atual
    jr_atual = _calcular_jr_por_is(pl_inicial, is_atual_percentual)
    sr_atual = _calcular_sr_por_jr_pl(pl_inicial, jr_atual)
    
    # Resolve a equação: (JR + x) / (PL + x) = IS_desejado
    # (JR + x) = IS_desejado * (PL + x)
    # JR + x = IS_desejado * PL + IS_desejado * x
    # JR + x - IS_desejado * x = IS_desejado * PL
    # JR + x * (1 - IS_desejado) = IS_desejado * PL
    # x * (1 - IS_desejado) = IS_desejado * PL - JR
    # x = (IS_desejado * PL - JR) / (1 - IS_desejado)
    
    numerador = is_desejado_decimal * pl_inicial - jr_atual
    denominador = 1 - is_desejado_decimal
    
    if denominador == 0:
        raise ValueError("IS desejado não pode ser 100%")
    
    x = numerador / denominador
    
    # Calcula os novos valores
    jr_novo = jr_atual + x
    pl_novo = pl_inicial + x
    sr_novo = sr_atual  # SR permanece o mesmo
    
    # Verifica o cálculo
    is_verificacao = (jr_novo / pl_novo) * 100
    
    return {
        'pl_inicial': pl_inicial,
        'jr_inicial': jr_atual,
        'sr_inicial': sr_atual,
        'is_inicial_decimal': is_atual_decimal,
        'is_inicial_percentual': is_atual_percentual,
        'adicional_x': x,
        'jr_final': jr_novo,
        'pl_final': pl_novo,
        'sr_final': sr_novo,
        'is_final_decimal': is_desejado_decimal,
        'is_final_percentual': is_verificacao,
        'is_desejado_decimal': is_desejado_decimal,
        'is_desejado_percentual': is_desejado_percentual
    }


class CalculusLogic:
    """
    Lógica principal para cálculos de IS
    """
    
    @staticmethod
    def calculate_is(pl, jr):
        """
        Calcula IS atual
        """
        return _calcular_is_atual(pl, jr)
    
    @staticmethod
    def calculate_jr(pl, is_percentual):
        """
        Calcula JR baseado no IS desejado
        """
        return _calcular_jr_por_is(pl, is_percentual)
    
    @staticmethod
    def calculate_adicional_is(pl_inicial, is_atual_decimal, is_desejado_decimal):
        """
        Calcula adicional necessário para atingir IS desejado
        Args:
            is_atual_decimal: IS atual em decimal (ex: 0.15 para 15%)
            is_desejado_decimal: IS desejado em decimal (ex: 0.20 para 20%)
        """
        return _calcular_adicional_para_is_desejado(pl_inicial, is_atual_decimal, is_desejado_decimal)


def _exemplo_calculo():
    """
    Exemplo prático: PL=100, IS atual=15%, IS desejado=20%
    """
    pl = 100
    is_atual = 0.15  # 15%
    is_desejado = 0.20  # 20%
    
    resultado = CalculusLogic.calculate_adicional_is(pl, is_atual, is_desejado)
    
    print("=== CÁLCULO DE AJUSTE DE IS ===")
    print(f"PL inicial: {resultado['pl_inicial']:.2f}")
    print(f"JR inicial: {resultado['jr_inicial']:.2f}")
    print(f"SR inicial: {resultado['sr_inicial']:.2f}")
    print(f"IS inicial: {resultado['is_inicial_percentual']:.2f}%")
    print()
    print(f"IS desejado: {resultado['is_desejado_percentual']:.2f}%")
    print(f"Valor a adicionar (x): {resultado['adicional_x']:.2f}")
    print()
    print("=== RESULTADO FINAL ===")
    print(f"JR final: {resultado['jr_final']:.2f}")
    print(f"PL final: {resultado['pl_final']:.2f}")
    print(f"SR final: {resultado['sr_final']:.2f}")
    print(f"IS final: {resultado['is_final_percentual']:.2f}%")


if __name__ == "__main__":
    _exemplo_calculo()