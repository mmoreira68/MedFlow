from django.db import models
from .utils.text import normalize_sans_accents

class UniqueNormalizedNameMixin(models.Model):
    """
    Para entidades onde nome deve ser único ignorando acento/caixa.
    """
    nome = models.CharField(max_length=120)
    nome_norm = models.CharField(max_length=160, editable=False, db_index=True, unique=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        self.nome_norm = normalize_sans_accents(self.nome)

    def save(self, *args, **kwargs):
        self.nome_norm = normalize_sans_accents(self.nome)
        return super().save(*args, **kwargs)


class NormalizedNameMixin(models.Model):
    """
    Para entidades onde nome pode repetir (ex.: Profissional), mas
    ainda queremos manter a versão normalizada para busca/consistência.
    """
    nome = models.CharField(max_length=120)
    nome_norm = models.CharField(max_length=160, editable=False, db_index=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        self.nome_norm = normalize_sans_accents(self.nome)

    def save(self, *args, **kwargs):
        self.nome_norm = normalize_sans_accents(self.nome)
        return super().save(*args, **kwargs)
