from django.db import models
from src.common import abstract_models
from src.common.constant import PacketType


class QuizzTypeQuerySet(abstract_models.AbstractQuerySet):
    pass


class QuizzTypeManager(models.Manager):
    def get_ent(self):
        return self.get(name_code='ent')


class QuizzType(
    abstract_models.UUID,
    abstract_models.AbstractBaseName,
    abstract_models.AbstractBaseNameCode,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    icon = models.FileField(upload_to='quiz-type', null=True, blank=True)
    color = models.CharField(max_length=128)
    quizz_duration = models.DurationField(null=True, blank=True)

    objects = QuizzTypeManager.from_queryset(QuizzTypeQuerySet)()

    class Meta:
        db_table = 'common\".\"quizz_type'
        ordering = ['order']

    def __str__(self):
        return f"{self.name_code}"


class CourseTypeQuizzQuerySet(abstract_models.AbstractQuerySet):
    def get_all_active(self):
        return self.filter(
            quizz_type__is_active=True,
            course_type__is_active=True
        )


class CourseTypeQuizzManager(models.Manager):
    pass


class CourseTypeQuizz(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel
):
    course_type = models.ForeignKey(
        'common.CourseType',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_quizzes',
    )
    quizz_type = models.ForeignKey(
        'common.QuizzType',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_quizzes'
    )
    main = models.BooleanField(default=False)
    questions_number = models.IntegerField(default=0)

    objects = CourseTypeQuizzManager.from_queryset(CourseTypeQuizzQuerySet)()

    class Meta:
        unique_together = ('course_type', 'quizz_type')
        db_table = 'common\".\"course_type_quizz'

    def __str__(self):
        return f"{self.quizz_type.name_code}"


class Packet(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.IsActive,
    abstract_models.TimeStampedModel
):
    quizz_type = models.ForeignKey(
        'common.CourseTypeQuizz',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_quizzes'
    )
    days = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    packet_type = models.CharField(
        choices=PacketType.choices(),
        default=PacketType.ONE_TIME
    )
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'common\".\"packet'
