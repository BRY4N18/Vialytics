class SeveridadService:
    LEVE = 1
    MODERADO = 2
    GRAVE = 3
    FATAL = 4

    @staticmethod
    def calcular(numheridos: int, numfallecidos: int, numvehiculos: int) -> int:
        if numfallecidos > 0:
            return SeveridadService.FATAL
        if numheridos >= 3 or numvehiculos >= 4:
            return SeveridadService.GRAVE
        if numheridos >= 1 or numvehiculos >= 2:
            return SeveridadService.MODERADO
        return SeveridadService.LEVE
