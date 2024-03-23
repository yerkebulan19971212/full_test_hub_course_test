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
    abstract_models.TimeStampedModel,
    abstract_models.Deleted,
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

    def get_all_active_without_rating(self):
        return self.filter(
            quizz_type__is_active=True,
            course_type__is_active=True
        ).exclude(quizz_type__name_code='rating')


class CourseTypeQuizzManager(models.Manager):
    pass


class CourseTypeQuizz(
    abstract_models.UUID,
    abstract_models.Ordering,
    abstract_models.TimeStampedModel,
    abstract_models.Deleted,
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
    abstract_models.AbstractBaseNameCode,
    abstract_models.TimeStampedModel
):
    name_kz = models.CharField(max_length=255, default='', blank=True)
    name_ru = models.CharField(max_length=255, default='', blank=True)
    name_en = models.CharField(max_length=255, default='', blank=True)
    quizz_type = models.ForeignKey(
        'common.CourseTypeQuizz',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='course_type_quizzes'
    )
    days = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    second_price = models.IntegerField(default=0)
    img = models.FileField(null=True, blank=True)
    packet_type = models.CharField(
        choices=PacketType.choices(),
        default=PacketType.ONE_TIME
    )
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'common\".\"packet'

    def __str__(self):
        return f'{self.name_code} - {self.name_ru}'


class RatingTest(
    abstract_models.UUID,
    abstract_models.TimeStampedModel,
):
    start_time = models.DateField()
    end_time = models.DateField()

    class Meta:
        db_table = 'common\".\"rating_test'

    def __str__(self):
        return f"{str(self.start_time)} - {str(self.end_time)}"


class BoughtPacket(
    abstract_models.UUID,
    abstract_models.TimeStampedModel
):
    user = models.ForeignKey(
        'accounts.User',
        related_name='bought_packets',
        on_delete=models.CASCADE,
        db_index=True,
        null=True
    )
    packet = models.ForeignKey(
        'common.Packet',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='bought_packets'
    )
    rating_test = models.ForeignKey(
        'common.RatingTest',
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
        related_name='bought_packets'
    )
    remainder = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    price = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'common\".\"bought_packet'


class QuestionAnswerImage(abstract_models.TimeStampedModel):
    upload = models.ImageField(upload_to='image/')

    class Meta:
        db_table = 'common\".\"question_answer_image'

