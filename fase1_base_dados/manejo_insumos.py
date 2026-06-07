"""
FarmTech Solutions - Fase 7 | Pessoa 1
manejo_insumos.py - Doses de fertilizante e defensivos por talhao.
"""


def litros_por_linha(ruas, metros_por_rua, dose_ml_por_m):
    """Litros totais de insumo liquido aplicado nas linhas de plantio.

    Logica: ruas * metros_por_rua * (dose_mL_por_m / 1000), convertendo mL -> L.
    Ex.: 10 ruas * 100 m * 500 mL/m = 500.000 mL = 500 L
    """
    return ruas * metros_por_rua * (dose_ml_por_m / 1000)


def fertilizante_por_area(area_m2, dose_kg_por_ha):
    """Fertilizante (kg) a partir de uma dose por hectare. 1 ha = 10.000 m2."""
    hectares = area_m2 / 10_000
    return hectares * dose_kg_por_ha


if __name__ == "__main__":
    litros = litros_por_linha(25, 80, 400)
    print(f"Insumo liquido (25 ruas, 80 m/rua, 400 mL/m): {litros:.1f} L")
    fert = fertilizante_por_area(30000, 250)   # 30.000 m2 = 3 ha, a 250 kg/ha
    print(f"Fertilizante (3 ha a 250 kg/ha): {fert:.1f} kg")
