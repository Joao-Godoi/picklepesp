from django.db import models
from django.core.exceptions import ValidationError


class Double(models.Model):
    name = models.CharField("Nome", max_length=100)
    player_1 = models.CharField("Jogador 1", max_length=100)
    player_2 = models.CharField("Jogador 2", max_length=100)

    class Meta:
        verbose_name = "Dupla"
        verbose_name_plural = "Duplas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField("Nome", max_length=10, unique=True)
    doubles = models.ManyToManyField(
        Double,
        related_name="groups",
        verbose_name="Duplas",
        blank=True,
    )

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ["name"]

    def __str__(self):
        return f"Grupo {self.name}"


class Match(models.Model):
    PHASE_GROUP = "grupo"
    PHASE_SEMIFINAL = "semifinal"
    PHASE_FINAL = "final"
    PHASE_DISPUTE = "disputa"

    PHASE_CHOICES = [
        (PHASE_GROUP, "Grupo"),
        (PHASE_SEMIFINAL, "Semifinal"),
        (PHASE_FINAL, "Final"),
        (PHASE_DISPUTE, "Disputa"),
    ]

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FINISHED = "finished"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_IN_PROGRESS, "Em andamento"),
        (STATUS_FINISHED, "Finalizada"),
    ]

    phase = models.CharField("Tipo", max_length=20, choices=PHASE_CHOICES)
    status = models.CharField(
        "Status",
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    match_number = models.PositiveIntegerField("Numero do jogo", unique=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
        verbose_name="Grupo",
    )
    double_1 = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_as_double_1",
        verbose_name="Dupla 1",
    )
    double_2 = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_as_double_2",
        verbose_name="Dupla 2",
    )
    winner = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches_won",
        verbose_name="Vencedor",
    )
    source_match_1 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_as_double_1",
        verbose_name="Jogo de origem dupla 1",
        help_text="Partida que define a dupla 1 desta partida",
    )
    source_match_1_is_winner = models.BooleanField(
        "Dupla 1 e vencedora do jogo de origem",
        null=True,
        blank=True,
        help_text="True se dupla 1 vem do vencedor, False se do perdedor",
    )
    source_match_2 = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_as_double_2",
        verbose_name="Jogo de origem dupla 2",
        help_text="Partida que define a dupla 2 desta partida",
    )
    source_match_2_is_winner = models.BooleanField(
        "Dupla 2 e vencedora do jogo de origem",
        null=True,
        blank=True,
        help_text="True se dupla 2 vem do vencedor, False se do perdedor",
    )
    source_double_1_desc = models.CharField(
        "Descricao origem dupla 1",
        max_length=100,
        blank=True,
        default="",
    )
    source_double_2_desc = models.CharField(
        "Descricao origem dupla 2",
        max_length=100,
        blank=True,
        default="",
    )
    final_position_winner = models.PositiveIntegerField(
        "Posicao vencedor",
        null=True,
        blank=True,
    )
    final_position_loser = models.PositiveIntegerField(
        "Posicao perdedor",
        null=True,
        blank=True,
    )
    sort_order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["sort_order", "match_number"]

    def __str__(self):
        d1 = (
            self.source_double_1_desc
            or str(self.double_1)
            if self.double_1
            else "A definir"
        )
        d2 = (
            self.source_double_2_desc
            or str(self.double_2)
            if self.double_2
            else "A definir"
        )
        return f"Jogo {self.match_number}: {d1} vs {d2}"

    @property
    def best_of(self):
        if self.phase == self.PHASE_DISPUTE:
            return 1
        return 3

    @property
    def phase_label(self):
        labels = {
            1: "Disputa 12\u00ba ao 14\u00ba",
            2: "Disputa 12\u00ba ao 14\u00ba",
            3: "Disputa 9\u00ba ao 11\u00ba",
            4: "Disputa 9\u00ba ao 11\u00ba",
            5: "Quartas de Final",
            6: "Quartas de Final",
            7: "Quartas de Final",
            8: "Quartas de Final",
            9: "Disputa 5\u00ba ao 8\u00ba",
            10: "Disputa 5\u00ba ao 8\u00ba",
            11: "Disputa 7\u00ba e 8\u00ba",
            12: "Disputa 5\u00ba e 6\u00ba",
            13: "Semifinal",
            14: "Semifinal",
            15: "Disputa 3\u00ba e 4\u00ba",
            16: "Final",
        }
        if self.match_number >= 1000:
            return "Fase de Grupos"
        return labels.get(self.match_number, self.get_phase_display())

    def clean(self):
        errors = {}
        if self.double_1_id and self.double_2_id and self.double_1_id == self.double_2_id:
            errors["double_2"] = "Dupla 2 deve ser diferente de Dupla 1."
        if errors:
            raise ValidationError(errors)


class Set(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="sets",
        verbose_name="Partida",
    )
    set_number = models.PositiveIntegerField("Set")
    double_1 = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sets_as_double_1",
        verbose_name="Dupla 1",
    )
    double_2 = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sets_as_double_2",
        verbose_name="Dupla 2",
    )
    points_double_1 = models.PositiveIntegerField(
        "Pontos dupla 1",
        default=0,
    )
    points_double_2 = models.PositiveIntegerField(
        "Pontos dupla 2",
        default=0,
    )
    winner = models.ForeignKey(
        Double,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sets_won",
        verbose_name="Vencedor",
    )

    class Meta:
        verbose_name = "Set"
        verbose_name_plural = "Sets"
        ordering = ["match", "set_number"]
        unique_together = [["match", "set_number"]]

    def __str__(self):
        return (
            f"Set {self.set_number} - Jogo {self.match.match_number}: "
            f"{self.points_double_1}x{self.points_double_2}"
        )

    def clean(self):
        errors = {}
        if self.points_double_1 == self.points_double_2:
            if self.points_double_1 > 0:
                errors["points_double_1"] = "Set nao pode terminar empatado."
                errors["points_double_2"] = "Set nao pode terminar empatado."
        else:
            if self.points_double_1 < 11 and self.points_double_2 < 11:
                if self.points_double_1 > 0 or self.points_double_2 > 0:
                    errors["points_double_1"] = (
                        "Pelo menos um lado deve atingir 11 pontos."
                    )
                    errors["points_double_2"] = (
                        "Pelo menos um lado deve atingir 11 pontos."
                    )
            if self.points_double_1 > 11 or self.points_double_2 > 11:
                errors["points_double_1"] = (
                    "Pontuacao maxima por set e 11 pontos."
                )
                errors["points_double_2"] = (
                    "Pontuacao maxima por set e 11 pontos."
                )
        if self.match_id:
            best_of = self.match.best_of
            if self.set_number < 1 or self.set_number > best_of:
                errors["set_number"] = (
                    f"Numero do set deve estar entre 1 e {best_of}."
                )
        if errors:
            raise ValidationError(errors)
