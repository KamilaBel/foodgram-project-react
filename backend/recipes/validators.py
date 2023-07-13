from django.core.validators import RegexValidator

hex_color_regex = RegexValidator(
    regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
    message="Неверный формат цвета. ")
