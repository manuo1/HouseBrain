from django.db import models
from housebrain_config.settings.constants import (ERROR_IINST)

"""
/!\ Teleinformation comes from the French electric network, docstrings
/!\ on the models will be in French.
"""

class TeleinfoManager(models.Manager):
    def save_teleinfo(self, teleinfo):
        new_teleinfo_history = TeleinformationHistory()
        new_teleinfo_history.save()
        new_teleinfo_history = TeleinformationHistory(
            id=new_teleinfo_history.id, **teleinfo)
        new_teleinfo_history.save()

    def clear_all_teleinformation_history(self):
        TeleinformationHistory.objects.all().delete()

    def update_power_monitoring(self, new_monitoring):
        last_monitoring = self.get_last_power_monitoring()
        new_monitoring = PowerMonitoring(
            id=last_monitoring.id, **new_monitoring)
        new_monitoring.save()

    def save_critical_remaining_power(self, new_monitoring):
        new_monitoring = PowerMonitoring(**new_monitoring)
        new_monitoring.save()


    def get_last_power_monitoring(self):
        if PowerMonitoring.objects.exists():
            power_monitoring = PowerMonitoring.objects.latest('date_time')
        else:
            power_monitoring = PowerMonitoring()
            power_monitoring.save()
        return power_monitoring

class PowerMonitoring(models.Model):

    date_time = models.DateTimeField(auto_now=True)
    # Intensité instantanée : IINST
    # | ( 3 car. unité = ampères)
    IINST = models.SmallIntegerField(default=ERROR_IINST)
    ISOUSC = models.SmallIntegerField(default=ERROR_IINST)
    percentage_remaining_power = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.date_time:%d/%m/%Y %H:%M} | P > {self.percentage_remaining_power}%'


class TeleinformationHistory(models.Model):

    date_time = models.DateTimeField(null=True, blank=True)
    # Adresse du compteur : ADCO
    # | (12 caractères)
    ADCO = models.CharField(max_length=12)

    # Option tarifaire (type d’abonnement) : OPTARIF
    # | (4 car.)
    OPTARIF = models.CharField(max_length=4)

    # Intensité souscrite : ISOUSC
    # | ( 2 car. unité = ampères)
    ISOUSC = models.CharField(max_length=2)

    # Index si option = base : BASE
    # | ( 9 car. unité = Wh)
    BASE = models.CharField(max_length=9)

    # Index heures creuses si option = heures creuses : HCHC
    # | ( 9 car. unité = Wh)
    HCHC = models.CharField(max_length=9)

    # Index heures pleines si option = heures creuses : HCHP
    # | ( 9 car. unité = Wh)
    HCHP = models.CharField(max_length=9)

    # Index heures normales si option = EJP : EJP HN
    # | ( 9 car. unité = Wh)
    EJPHN = models.CharField(max_length=9)

    # Index heures de pointe mobile si option = EJP : EJP HPM
    # | ( 9 car. unité = Wh)
    EJPHPM = models.CharField(max_length=9)

    # Index heures creuses jours bleus si option = tempo : BBR HC JB
    # | ( 9 car. unité = Wh)
    BBRHCJB = models.CharField(max_length=9)

    # Index heures pleines jours bleus si option = tempo : BBR HP JB
    # | ( 9 car. unité = Wh)
    BBRHPJB = models.CharField(max_length=9)

    # Index heures creuses jours blancs si option = tempo : BBR HC JW
    # | ( 9 car. unité = Wh)
    BBRHCJW = models.CharField(max_length=9)

    # Index heures pleines jours blancs si option = tempo : BBR HP JW
    # | ( 9 car. unité = Wh)
    BBRHPJW = models.CharField(max_length=9)

    # Index heures creuses jours rouges si option = tempo : BBR HC JR
    # | ( 9 car. unité = Wh)
    BBRHCJR = models.CharField(max_length=9)

    # Index heures pleines jours rouges si option = tempo : BBR HP JR
    # | ( 9 car. unité = Wh)
    BBRHPJR = models.CharField(max_length=9)

    # Préavis EJP si option = EJP : PEJP
    # | ( 2 car.) 30mn avant période EJP
    PEJP = models.CharField(max_length=2)

    # Période tarifaire en cours : PTEC
    # | ( 4 car.)
    PTEC = models.CharField(max_length=4)

    # Couleur du lendemain si option = tempo : DEMAIN
    # | ( 4 car.)
    DEMAIN = models.CharField(max_length=4)

    # Intensité instantanée : IINST
    # | ( 3 car. unité = ampères)
    IINST = models.CharField(max_length=3)

    # Avertissement de dépassement de puissance souscrite : ADPS
    # | ( 3 car. unité = ampères) (message émis uniquement en cas de
    # | dépassement effectif, dans ce cas il est immédiat)
    ADPS = models.CharField(max_length=3)

    # Intensité maximale : IMAX
    # | ( 3 car. unité = ampères)
    IMAX = models.CharField(max_length=3)

    # Puissance apparente : PAPP
    # | ( 5 car. unité = Volt.ampères)
    PAPP = models.CharField(max_length=5)

    # Groupe horaire si option = heures creuses ou tempo : HHPHC
    # | (1 car.)
    HHPHC = models.CharField(max_length=1)

    # Mot d’état (autocontrôle) : MOTDETAT
    # | (6 car.)
    MOTDETAT = models.CharField(max_length=6)

    def __str__(self):
        return f'{self.ADCO} | {self.date_time:%d/%m/%Y %H:%M}'
