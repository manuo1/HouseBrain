from django.db import models, IntegrityError
from rooms.models import Room

class TemperatureSensorManager(models.Manager):
    def add_sensors(self, sensor_folder_paths):
        for path in sensor_folder_paths:
            temperature_sensor = TemperatureSensor(sensor_folder_path = path)
            try:
                temperature_sensor.save()
            except IntegrityError:
                pass

    def all_sensor_list(self):
        list = TemperatureSensor.objects.all().order_by(
            'name', 'sensor_folder_path'
        )
        return list

    def save_temperature(self, new_temperature, sensor):
        if self.temperature_is_valid(new_temperature):
            new_temperature_history = TemperatureHistory(
                temperature = new_temperature,
                associated_sensor = sensor
            )
            new_temperature_history.save()

    def temperature_is_valid(self, new_temperature):
        if new_temperature not in range(-5000,6000):
            return False
        return True

    def get_sensor_temperatures(self, sensor):
        sensor_temperatures_list = TemperatureHistory.objects.filter(
            associated_sensor=sensor).order_by('-date_time')
        return sensor_temperatures_list

class TemperatureSensor(models.Model):

    name = models.CharField(
        default="unnamed",
        max_length=100
    )
    sensor_folder_path = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    associated_room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        room_name = "(?)"
        if self.associated_room:
            room_name = self.associated_room.name
        ret = "{} | {} ({})".format(
            room_name,
            self.name,
            self.sensor_folder_path[-15:],
        )
        return ret

class TemperatureHistory(models.Model):
    temperature = models.IntegerField()
    date_time = models.DateTimeField(
        auto_now_add=True
    )
    associated_sensor = models.ForeignKey(
        TemperatureSensor,
        on_delete=models.CASCADE
    )

    def __str__(self):
        room_name = "(?)"
        if self.associated_sensor.associated_room:
            room_name = self.associated_sensor.associated_room.name

        ret = "{} | {} ({}) | {} | {}".format(
            room_name,
            self.associated_sensor.name,
            self.associated_sensor.sensor_folder_path[-15:],
            f'{self.date_time:%d/%m/%Y %H:%M}',
            f'{(self.temperature/1000):.2f}°C'
        )
        return ret
