from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.utils import timezone

# ER-Modelle

# Layout modell, Layout for page to choose and only developer can make data entries
class Layout(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    template = models.TextField()

class LayoutRegion(models.Model):
    id = models.AutoField(primary_key=True)
    layout_id = models.ForeignKey(Layout, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=200)

# Design modell for page to choose
class Design(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    font_family = models.CharField(max_length=200)
    primary_color = models.CharField(max_length=200)
    secondary_color = models.CharField(max_length=200)
    background_color = models.CharField(max_length=200)
    # optional settings
    border_radius = models.IntegerField(blank=True, null=True)
    content_width = models.IntegerField(blank=True, null=True)
    content_height = models.IntegerField(blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    font_size = models.IntegerField(blank=True, null=True)
    font_color = models.CharField(max_length=200)
    # safe customized css (new data entries only possible for developer)
    custom_css = models.TextField(blank=True)

class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    status = models.BooleanField(default=False)

    layout_id = models.ForeignKey(
        Layout,
        on_delete=models.CASCADE,
        related_name='layouts'
    )

    design_id = models.ForeignKey(
        Design,
        on_delete=models.CASCADE,
        related_name='designs'
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PageVersion(models.Model):
    id = models.AutoField(primary_key=True)
    page_id = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='owns')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
    status = models.BooleanField(default=True)
    published_at = models.DateTimeField(blank=True, null=True)

class NavigationItem(models.Model):
    id = models.AutoField(primary_key=True)
    page_id = models.ForeignKey(Page, on_delete=models.CASCADE, related_name = 'linksTo')

    parent_id = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name='children',
        blank=True, null=True
    )

    title = models.CharField(max_length=200)
    position = models.IntegerField(blank=True, null=True)
    visible = models.BooleanField(default=True)

class Block(models.Model):
    id = models.AutoField(primary_key=True)
    block_type = models.CharField(max_length=200)
    config = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CmsMedium(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='media/cms')
    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=200)
    alt_text = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Function(models.Model):
    id = models.AutoField(primary_key=True)

    FUNCTION_TYPES = [
        ('news', 'News'),
        ('announcement', 'Announcement'),
        ('calender', 'Calender'),
        ('forum', 'Forum'),
        ('lunch', 'Lunch'),
        ('quiz', 'Quiz'),
        ('learning Materials', 'Learning Materials'),
        ('school pictures', 'School Pictures'),
        ('careers', 'Careers'),
        ('ai chat', 'AI Chat'),
        ('classes', 'Classes'),
        ('grades', 'Grades'),]
    function_type = models.CharField(max_length=200, choices=FUNCTION_TYPES, unique=True)
    code = models.TextField()
    active = models.BooleanField(default=True)

class PageBlock(models.Model):
    id = models.AutoField(primary_key=True)
    page_version_id = models.ForeignKey(PageVersion, on_delete=models.CASCADE, related_name='pageBlocks')
    block_id = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='pageBlocks')
    layout_region_id = models.ForeignKey(LayoutRegion, on_delete=models.CASCADE, related_name='pageBlocks')
    position = models.IntegerField()

class BlockMedium(models.Model):
    id = models.AutoField(primary_key=True)
    block_id = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='blockMedia')
    medium_id = models.ForeignKey(CmsMedium, on_delete=models.CASCADE, related_name='mediumBlocks')
    position = models.IntegerField()

class FunctionBlock(models.Model):
    id = models.AutoField(primary_key=True)
    function_id = models.ForeignKey(Function, on_delete=models.CASCADE, related_name='functionBlocks')
    block_id = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='functionBlocks')
    config = JSONField(blank=True, null=True)

class Publication(models.Model):
    id = models.AutoField(primary_key=True)
    page_version_id = models.ForeignKey(PageVersion, on_delete=models.CASCADE, related_name='published')
    published_at = models.DateTimeField(auto_now_add=True)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)