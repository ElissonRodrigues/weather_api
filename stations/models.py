from django.db import models

class Station(models.Model):
    station_id = models.IntegerField(primary_key=True)
    station_name = models.TextField()
    city = models.TextField()
    owner = models.TextField(null=True, blank=True)  # Proprietário da estação
    latitude = models.TextField(blank=True, null=True)  # Latitude da estação
    longitude = models.TextField(blank=True, null=True)  # Longitude da estação
    uf = models.CharField(max_length=2, blank=True, null=True)  # Unidade federativa (estado)

    def __str__(self):
        return self.name


class RegistrationData(models.Model):
    station_id = models.ForeignKey(Station, related_name='RegistrationData', on_delete=models.CASCADE)  # Chave estrangeira para Station  
    DataHora_GMT = models.DateTimeField(blank=True, null=True)  # Data e hora no formato GMT
    Bateria_volts = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Voltagem da bateria
    ContAguaSolo100_m3 = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Contagem de água no solo com 100 metros cúbicos
    ContAguaSolo200_m3 = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Contagem de água no solo com 200 metros cúbicos
    ContAguaSolo400_m3 = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Contagem de água no solo com 400 metros cúbicos
    CorrPSol_logico = models.BooleanField(null=True, blank=True)  # Corrente do painel solar
    DirVelVentoMax_oNV = models.TextField(null=True, blank=True)  # Direção da velocidade máxima do vento
    dirVento_oNV = models.TextField(null=True, blank=True)  # Direção do vento
    NivMare_m = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Nível do mar
    hora = models.TimeField(null=True, blank=True)  # Hora do registro
    NivRegua_m = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Nível da régua
    Pluvio_mm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Pluviômetro
    PressaoAtm_mb = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Pressão atmosférica
    RadSolAcum_MJm2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # Radiação solar acumulada
    RadSolGlob_Wm2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # Radiação solar global
    TempAr_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura do ar
    TempMax_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura máxima
    TempMin_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura mínima
    TempInt_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura interna
    TempSolo100_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura do solo com 100 metros
    TempSolo200_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura do solo com 200 metros
    TempSolo400_C = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Temperatura do solo com 400 metros
    UmidInt_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Umidade interna
    UmiRel_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Umidade relativa
    VelVento_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Velocidade do vento
    VelVento10m_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Velocidade do vento a 10 metros
    VelVentoMax_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Velocidade máxima do vento

    def __str__(self):
        return f"{self.station_id} - {self.DataHora_GMT}"
    
