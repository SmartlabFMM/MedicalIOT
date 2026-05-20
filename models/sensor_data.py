from odoo import models, fields

class SensorData(models.Model):
    _name = 'med.iot.sensor.data'
    _description = 'ESP32 Sensor Data'
    _order = 'timestamp desc'

    name        = fields.Char(default='ESP32 Reading')
    sensor_id   = fields.Char(string='Sensor ID')
    temperature = fields.Float(string='Temperature (°C)')
    humidity    = fields.Float(string='Humidity (%)')
    timestamp   = fields.Datetime(string='Timestamp', default=fields.Datetime.now)