from calendar import monthrange
from datetime import timedelta
from django.db import models
from django.utils import timezone
from housebrain_config.settings.constants import (
    ERROR_IINST,
    PRICE_PER_KILOWATT_HOUR_HP as price_hp,
    PRICE_PER_KILOWATT_HOUR_HC as price_hc,
    MONTHLY_SUBSCRIPTION_PRICE as subscription_price,
)
from sensors.models import TemperatureSensorManager

temperature_sensor_manager = TemperatureSensorManager()

"""
/!\ Teleinformation comes from the French electric network, docstrings
/!\ on the models TeleinformationHistory will be in French.
"""

class TeleinfoManager(models.Manager):

    def save_teleinfo(self, teleinfo):
        if teleinfo["date_time"].minute != self.last_teleinfo_minute():
            new_teleinfo_history = TeleinformationHistory()
            new_teleinfo_history.save()
            new_teleinfo_history = TeleinformationHistory(
                id=new_teleinfo_history.id, **teleinfo)
            new_teleinfo_history.save()

    def delete_all_teleinformation_history(self):
        TeleinformationHistory.objects.all().delete()

    def update_power_monitoring(self, new):
        last = self.last_power_monitoring()
        monitoring = PowerMonitoring(id=last.id, **new)
        monitoring.save()
        """
        if new.is_malfunctioning != last.is_malfunctioning:
            self.save_a_new_power_monitoring(new)
        """
        if monitoring.ISOUC_is_exceeded != last.ISOUC_is_exceeded:
            self.save_a_new_power_monitoring(new)

    def save_a_new_power_monitoring(self, new_monitoring):
        monitoring = PowerMonitoring(**new_monitoring)
        monitoring.save()

    def last_teleinfo_minute(self):
        last_minute_saved = 5
        if TeleinformationHistory.objects.exists():
            last_teleinfo_history = TeleinformationHistory.objects.latest(
                    'date_time'
                )
            last_minute_saved = last_teleinfo_history.date_time.minute
        return last_minute_saved

    def last_power_monitoring(self):
        if PowerMonitoring.objects.exists():
            power_monitoring = PowerMonitoring.objects.latest('date_time')
        else:
            power_monitoring = PowerMonitoring()
            power_monitoring.save()
        return power_monitoring

    def daily_consumption(self, date):
        daily_consumption = {}
        daily_teleinfo = list(TeleinformationHistory.objects.filter(
            date_time__date = date,
        ).order_by('date_time'))
        midnight_teleinfo_of_the_next_day = (
            TeleinformationHistory.objects.filter(
                date_time__date = date + timedelta(days=1),
                date_time__hour = 0,
                date_time__minute = 0,
            )
        )
        if daily_teleinfo:
            if midnight_teleinfo_of_the_next_day:
                daily_teleinfo.append(midnight_teleinfo_of_the_next_day[0])
            if self.all_optarif(daily_teleinfo, "HC.." ):
                daily_consumption = {
                    "OPTARIF": "HC..",
                    "date": date,
                    "values" : {},
                }
                start_hc = self.str_to_int(daily_teleinfo[0].HCHC)
                end_hc = self.str_to_int(daily_teleinfo[-1].HCHC)
                start_hp = self.str_to_int(daily_teleinfo[0].HCHP)
                end_hp = self.str_to_int(daily_teleinfo[-1].HCHP)
                if all([values != 0 for values in [start_hc,end_hc,start_hp,end_hp]]):
                    hc = end_hc - start_hc
                    hp = end_hp - start_hp
                    percentage_hc = 50
                    if not hc+hp == 0:
                        percentage_hc = int((hc/(hc+hp))*100)
                    days_in_month = monthrange(date.year, date.month)[1]
                    price = ( hc/1000*price_hc
                            + hp/1000*price_hp
                            + subscription_price/days_in_month
                    )
                    heating_need = (
                        temperature_sensor_manager.heating_need_of_the_day(date)
                    )
                    daily_consumption["values"] = {
                        "HC": f'{round(hc/1000,1):.1f} kWh ({percentage_hc}%)',
                        "HP": f'{round(hp/1000,1):.1f} kWh ({100-percentage_hc}%)',
                        "???" : f'{round((hc+hp)/1000,1):.1f} kWh',
                        "#??" : f'{round(heating_need/1000)}??',
                        "???" : f'{round(price,2):.2f}???',
                    }

        return daily_consumption


    def str_to_int(self,str):
        try:
            return int(str)
        except (TypeError, ValueError):
            return 0


    def all_optarif(self, set, value):
        return all([teleinfo.OPTARIF == value for teleinfo in set])



class PowerMonitoring(models.Model):

    date_time = models.DateTimeField(auto_now=True)
    IINST = models.SmallIntegerField(default=ERROR_IINST)
    ISOUSC = models.SmallIntegerField(default=ERROR_IINST)
    is_malfunctioning = models.BooleanField(default=False)
    ISOUC_is_exceeded = models.BooleanField(default=False)

    def __str__(self):
        state = intensity = "OK"
        if self.is_malfunctioning:
            state = "! PB !"
        if self.ISOUC_is_exceeded:
            intensity = "! PB !"

        ret = (
            f'{self.date_time:%d/%m/%Y %H:%M:%S}'
            f' - {self.IINST}/{self.ISOUSC} A'
            f' - Teleinfo = {state} - Intensity = {intensity}'
        )
        return ret


class TeleinformationHistory(models.Model):

    date_time = models.DateTimeField(null=True, blank=True)
    # Adresse du compteur : ADCO
    # | (12 caract??res)
    ADCO = models.CharField(max_length=12)

    # Option tarifaire (type d???abonnement) : OPTARIF
    # | (4 car.)
    OPTARIF = models.CharField(max_length=4)

    # Intensit?? souscrite : ISOUSC
    # | ( 2 car. unit?? = amp??res)
    ISOUSC = models.CharField(max_length=2)

    # Index si option = base : BASE
    # | ( 9 car. unit?? = Wh)
    BASE = models.CharField(max_length=9)

    # Index heures creuses si option = heures creuses : HCHC
    # | ( 9 car. unit?? = Wh)
    HCHC = models.CharField(max_length=9)

    # Index heures pleines si option = heures creuses : HCHP
    # | ( 9 car. unit?? = Wh)
    HCHP = models.CharField(max_length=9)

    # Index heures normales si option = EJP : EJP HN
    # | ( 9 car. unit?? = Wh)
    EJPHN = models.CharField(max_length=9)

    # Index heures de pointe mobile si option = EJP : EJP HPM
    # | ( 9 car. unit?? = Wh)
    EJPHPM = models.CharField(max_length=9)

    # Index heures creuses jours bleus si option = tempo : BBR HC JB
    # | ( 9 car. unit?? = Wh)
    BBRHCJB = models.CharField(max_length=9)

    # Index heures pleines jours bleus si option = tempo : BBR HP JB
    # | ( 9 car. unit?? = Wh)
    BBRHPJB = models.CharField(max_length=9)

    # Index heures creuses jours blancs si option = tempo : BBR HC JW
    # | ( 9 car. unit?? = Wh)
    BBRHCJW = models.CharField(max_length=9)

    # Index heures pleines jours blancs si option = tempo : BBR HP JW
    # | ( 9 car. unit?? = Wh)
    BBRHPJW = models.CharField(max_length=9)

    # Index heures creuses jours rouges si option = tempo : BBR HC JR
    # | ( 9 car. unit?? = Wh)
    BBRHCJR = models.CharField(max_length=9)

    # Index heures pleines jours rouges si option = tempo : BBR HP JR
    # | ( 9 car. unit?? = Wh)
    BBRHPJR = models.CharField(max_length=9)

    # Pr??avis EJP si option = EJP : PEJP
    # | ( 2 car.) 30mn avant p??riode EJP
    PEJP = models.CharField(max_length=2)

    # P??riode tarifaire en cours : PTEC
    # | ( 4 car.)
    PTEC = models.CharField(max_length=4)

    # Couleur du lendemain si option = tempo : DEMAIN
    # | ( 4 car.)
    DEMAIN = models.CharField(max_length=4)

    # Intensit?? instantan??e : IINST
    # | ( 3 car. unit?? = amp??res)
    IINST = models.CharField(max_length=3)

    # Avertissement de d??passement de puissance souscrite : ADPS
    # | ( 3 car. unit?? = amp??res) (message ??mis uniquement en cas de
    # | d??passement effectif, dans ce cas il est imm??diat)
    ADPS = models.CharField(max_length=3)

    # Intensit?? maximale : IMAX
    # | ( 3 car. unit?? = amp??res)
    IMAX = models.CharField(max_length=3)

    # Puissance apparente : PAPP
    # | ( 5 car. unit?? = Volt.amp??res)
    PAPP = models.CharField(max_length=5)

    # Groupe horaire si option = heures creuses ou tempo : HHPHC
    # | (1 car.)
    HHPHC = models.CharField(max_length=1)

    # Mot d?????tat (autocontr??le) : MOTDETAT
    # | (6 car.)
    MOTDETAT = models.CharField(max_length=6)

    def __str__(self):
        return f'{self.ADCO} | {self.date_time:%d/%m/%Y %H:%M}'
