from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User as MyUser
from django.urls import reverse

from .api import (
    ProjectMapping,
    SampleMapping,
    OriginDataMapping,
    AnalysisDataMapping,
    DatafileMapping,
)

#class MyUser(AbstractUser):
    # Notice that we are inheriting from AbstractUser. Therefore, we                                                            
    # get all the default fields for free.                                                                                      
#    organization = models.CharField(max_length=255, default="")
#    name_identifier = models.CharField(max_length=255, default="")
#    identifier_scheme = models.CharField(max_length=255, default="")
#    scheme_uri = models.CharField(max_length=255, default="")

#    def full_name(self):
#        return '%s %s' % (self.first_name, self.last_name)

#    def official_name(self):
#        return '%s, %s' % (self.last_name, self.first_name)

#    def APA_name(self):  # pylint: disable=invalid-name                                                                       #  
#        return '%s, %s.' % (self.last_name, self.first_name[0])

#    def IEEE_name(self):  # pylint: disable=invalid-name                                                                      #  
#        return '%s. %s' % (self.first_name[0], self.last_name)
#
#    def __unicode__(self):
#        return '%s (%s)' % (self.full_name(), self.organization)

def project_cover_pic_path(instance, filename):
    return '/'.join(['projects', str(instance.id), 'cover_pic', filename])


# Create your models here.
IMAGE_TYPES = (
    ('8-bit', '8-bit'),
    ('16-bit Signed', '16-bit Signed'),
    ('16-bit Unsigned', '16-bit Unsigned'),
    ('32-bit Signed', '32-bit Signed'),
    ('32-bit Unsigned', '32-bit Unsigned'),
    ('32-bit Real', '32-bit Real'),
    ('64-bit Real', '64-bit Real'),
    ('24-bit RGB', '24-bit RGB'),
    ('24-bit RGB Planar', '24-bit RGB Planar'),
    ('24-bit BGR', '24-bit BGR'),
    ('24-bit Integer', '24-bit Integer'),
    ('32-bit ARGB', '32-bit ARGB'),
    ('32-bit ABGR', '32-bit ABGR'),
    ('1-bit Bitmap', '1-bit Bitmap'),
)


BYTE_ORDERS = (
    ('big-endian', 'Big endian'),
    ('little-endian', 'Little endian'),
)

class project(models.Model):  # pylint: disable=invalid-name
    # Name of the project and user should be primary key,
    # but a composite primary key is not supported by
    # Django. Therefore, we would define a unique key
    # constraint for this.
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    creation_date = models.DateField()
    description = models.TextField()
    cover_pic = models.ImageField(upload_to=project_cover_pic_path, blank=True)
    #access = models.IntegerField(default=2, choices=ACCESS)
    #institution = models.CharField(max_length=255)
    #doi = models.CharField(max_length=512, blank=True)
    #ark = models.CharField(max_length=512, blank=True)
    #license = models.IntegerField(default=0, choices=LICENSES)
    #num_downloads = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "name",)
        ordering = ('name', '-creation_date', )

    def __unicode__(self):
        return self.name

    #@property
    #def doi_clean(self):
    #    doi = self.doi.strip()
    #    if self.doi.strip().startswith('doi:'):
    #        doi = doi.replace('doi:', '', 1)
    #    return doi

    def is_viewable_by_user(self, user):
        return True
    #    if user.is_superuser:
    #        return True
    #    elif user.has_perm('upload.change_project'):
    #        return True
    #    elif (self.access == 1 or
    #          user == self.user or
    #          self.is_collaborator(user)):
    #        return True
    #    return False

    def is_editable_by_user(self, user):
        return True
    #    if user.is_superuser:
    #         return True
    #     elif user.has_perm('upload.change_project'):
    #         return True
    #     elif (self.access == 2 and
    #           (user == self.user or
    #            self.is_collaborator(user))):
    #         return True
    #     return False

    def is_collaborator(self, user):
        return True
    #    for collab in self.collaborators.all():
    #        if user == collab.user:
    #            return True
    #    return False

    def delete(self, *args, **kwargs):
        # self._ezid_doi_delete()
        super(project, self).delete(*args, **kwargs)

    def origin_data_without_sample(self):
        return self.origin_data.filter(sample=None)

    # pylint: disable=invalid-name
    def analysis_data_without_sample_or_origin(self):
        return self.analysis_data.filter(sample=None, base_origin_data=None)


def project_file_path(instance, filename):
    project_id = instance.project.id
    dataset_type = 'origin'
    dataset_id = instance.origin_data.id

    return '/'.join([
        'projects',
        str(project_id),
        dataset_type,
        str(dataset_id),
        'images',
        filename
    ])


class sample(models.Model):
    SOURCES = (
        ('N', 'Natural'),
        ('A', 'Artificial')
    )

    POROUS_MEDIA_TYPE = (('SAND', 'Sandstone'),
                         ('SOIL', 'Soil'),
                         ('CARB', 'Carbonate'),
                         ('GRAN', 'Granite'),
                         ('BEAD', 'Beads'),
                         ('FIBR', 'Fibrous Media'),
                         ('COAL', 'Coal'),
                         ('OTHE', 'Other'))

    name = models.CharField(max_length=255)
    description = models.TextField()

    project = models.ForeignKey(project, related_name='samples', on_delete=models.CASCADE)
    uploader = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    porous_media_type = models.CharField(
        max_length=50,
        choices=POROUS_MEDIA_TYPE
    )
    porous_media_other_description = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Other porous media type description.',
    )
    source = models.CharField(max_length=50, choices=SOURCES)
    grain_size_min = models.FloatField(null=True, blank=True)
    grain_size_max = models.FloatField(null=True, blank=True)
    grain_size_avg = models.FloatField(null=True, blank=True)
    porosity = models.FloatField(null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    geographic_origin = models.CharField(
        max_length=50, null=True, blank=True,
        help_text=(
            'The geographic location, latitude/longitude, '
            'from which the sample was obtained.'
        ),
    )
    location = models.CharField(
        max_length=50, null=True, blank=True,
        help_text=(
            'This should be the current location of the sample. '
            'For example: which campus, building number, '
            'room number, and/or cabinet number.'
        ),
    )

    class Meta:
        unique_together = ("name", "project")

    def __unicode__(self):
        return self.name


class origin_data(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(project, related_name='origin_data', on_delete=models.CASCADE)
    sample = models.ForeignKey(
        sample,
        null=True,
        blank=True,
        help_text=(
            'Each data-set is associated with '
            'actual physical sample. Choose one of the existing '
            'sample, or add details for a new sample later.'
        ),
        related_name='origin_data',
        on_delete=models.CASCADE
    )
    uploader = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    is_segmented = models.IntegerField(
        choices=(
            (1, 'Yes'),
            (2, 'No')
        ),
        default=1
    )
    external_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='External URI'
        )
    voxel_x = models.FloatField(null=True, blank=True)
    voxel_y = models.FloatField(null=True, blank=True)
    voxel_z = models.FloatField(null=True, blank=True)
    voxel_units = models.CharField(
        max_length=50,
        blank=True,
        choices=(
            ('nm', 'nanometer'),
            ('um', 'micrometer'),
            ('mm', 'millimeter'),
            ('other', 'other (specify)')
            )
        )

    voxel_other = models.CharField(max_length=50, null=True, blank=True)
    provenance = models.TextField(verbose_name='Description')
    doi = models.CharField(max_length=255, blank=True)

    class Meta:
        # This is a caution, we don't have sample inside here.
        # This is intentional as we could have *unknown* sample.
        unique_together = ("name", "project",)
        verbose_name = 'Origin Data'
        verbose_name_plural = 'Origin Data'

    def __unicode__(self):
        return self.name


class analysis_data(models.Model):
    ANALYSIS_DATA_TYPE = (('Simulation', 'Simulation'),
                          ('GeometricAnalysis', 'Geometric Analysis'),
                          ('Other', 'Other'))

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=ANALYSIS_DATA_TYPE)

    project = models.ForeignKey(project, related_name='analysis_data', on_delete=models.CASCADE)
    sample = models.ForeignKey(sample, blank=True, null=True,
                               related_name='analysis_data', on_delete=models.CASCADE)
    uploader = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    external_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='External URI'
        )

    base_origin_data = models.ForeignKey(origin_data, blank=True, null=True,
                                         related_name='analysis_data', on_delete=models.CASCADE)
    base_analysis_data = models.ForeignKey(
        "analysis_data",
        blank=True,
        null=True,
        related_name='derived_analysis_data',
        on_delete=models.CASCADE
    )
    base_data_url = models.CharField(max_length=255)

    description = models.TextField()
    doi = models.CharField(max_length=255, blank=True)

    class Meta:
        # TODO :- Fix this. Sample problem as the origin data.
        unique_together = ("name", "project",)
        verbose_name = 'Analysis Data'
        verbose_name_plural = 'Analysis Data'

    def __unicode__(self):
        return self.name

class DataFile(models.Model):
    """
    A file in the system. Use this as foreign key to refer to metadata.
    """

    file = models.FileField(upload_to=project_file_path)
    # TODO: You can add related name to refer back from the referred table.
    origin_data = models.ForeignKey(origin_data, null=True, blank=True,
                                    related_name='allfiles', on_delete=models.CASCADE)
    analysis_data = models.ForeignKey(analysis_data, null=True, blank=True,
                                      related_name='allfiles', on_delete=models.CASCADE)
    uploader = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    isNonImageFile = models.BooleanField(default=False)
    isAdvancedImageFile = models.BooleanField(default=False)
    isNormalImageFile = models.BooleanField(default=False)

    class Meta:
        ordering = ('file',)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.file_name()

    @property
    def advanced_image(self):
        try:
            ret = AdvancedImageFile.objects.get(
                file=self.file,
                origin_data=self.origin_data,
                analysis_data=self.analysis_data
            )
        except AdvancedImageFile.DoesNotExist:
            return None

        return ret

    def file_name(self):
        return os.path.basename(self.file.name)

    def file_size(self):
        try:
            return self.file.size
        except Exception:  # pylint: disable=broad-except
            return None

    def is_advanced(self):
        if not re.search(
                'gif|jpe?g|png|tiff?$',
                self.file_name(),
                flags=re.IGNORECASE
        ):
            return True
        return False

    def has_gif(self):
        gif_path = os.path.join(settings.MEDIA_ROOT, self.file.name + '.gif')
        if os.path.isfile(gif_path):
            return True
        return False

    def has_meta(self):
        try:
            return self.metadata is not None
        except ObjectDoesNotExist:
            return False

    def is_archive(self):
        archive_extensions = ['.zip'] # , '.zipx', '.ar', '.tar', '.bz2', '.gzip', '.gz', '.xz', '.7z', '.rar']
        return any(ext in self.file_name() for ext in archive_extensions)

    def has_histogram(self):
        gif_path = os.path.join(
            settings.MEDIA_ROOT,
            self.file.name + '.histogram.jpg'
        )
        if os.path.isfile(gif_path):
            return True
        return False

    def has_histogram_csv(self):
        gif_path = os.path.join(
            settings.MEDIA_ROOT,
            self.file.name + '.histogram.csv'
        )
        if os.path.isfile(gif_path):
            return True
        return False

    @property
    def agave_uri(self):
        return "agave://digitalrocks.repo.corral.storage/{}".format(
            self.file.name
        )


class NonImageFile(DataFile):

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.file_name()


class NormalImageFile(DataFile):

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.file_name()


class AdvancedImageFile(DataFile):
    image_type = models.CharField(max_length=50, null=True, blank=True,
                                  choices=IMAGE_TYPES)
    width = models.CharField(max_length=10, null=True, blank=True)
    height = models.CharField(max_length=10, null=True, blank=True)
    offsetToFirstImage = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name='Offset to First Image'
    )
    numberOfImages = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Number of Images'
    )
    gapBetweenImages = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Gap Between Images'
    )
    byteOrder = models.CharField(
        max_length=15,
        choices=BYTE_ORDERS,
        null=True,
        blank=True,
        verbose_name='Byte Order'
    )
    use_binary_correction = models.BooleanField(
        default=True,
        help_text=(
            'If the image is rendered all black, then the RAW data '
            'is likely only zeroes and ones. Check this box to '
            'pin values to 0 and 255 so that image features are '
            'visible. This is non-destructive to the original '
            'image data.'
        )
    )
