from django.conf import settings
from django.contrib import messages, auth # auth for users_csv view, TODO: move to admin app
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
#from django.shortcuts import render_to_response
from django.template import loader, Context
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
import os
from datetime import datetime
from PIL import Image

from upload.forms import (AddProjectForm, AdvancedImageUploadForm, OriginDataForm, AnalysisDataForm, SampleDataForm, DataFileUploadForm)
from upload.models import (project, origin_data)

#    AccountProfileForm, AddProjectForm, ProjectEditForm, PublicationForm,
#                    OriginDataForm, AnalysisDataForm, SampleDataForm,
#                    AdvancedImageUploadForm, AdvancedImageEditForm,
#                    PublicationRequestForm, DataFileUploadForm,
#                    FeedbackForm)


#from upload.api import search_query

# Create your views here.

def my_projects(request):
    """
    This would direct a user to page having list of their projects, also
    includes collaboration projects.

    Same function would be invoked when user tries to add a new project.
    """
    list_of_projects = project.objects.filter(user=request.user)

    #collaboration_projects = []
    #collaborations = collaborator.objects.filter(user=request.user).exclude(project__user=request.user)
    #for coll in collaborations:
    #    collaboration_projects.append(coll.project)

    context = {
        'projects' : list_of_projects,}
    #    'collaboration_projects': collaboration_projects,}

    return render(request, 'upload/my_projects.html', context)


#@login_required
def create_project(request):
    if request.POST:
        form = AddProjectForm(request.POST, request.FILES)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.user = request.user
            #new_project.institution = request.user.organization
            new_project.creation_date = datetime.today()
            new_project.save()
            return HttpResponseRedirect(reverse('view_project', args=[new_project.id]))
    else:
        form = AddProjectForm()

    context = {'form': form}
    return render(request, 'upload/project/create_project.html', context)



def view_project(request, project_id, view_type=None):
    """
    View to render the project page.

    Visibility of the buttons to edit metadata, upload data and manage publications
    would be controlled from the template.

    """
    project_obj = project.objects.filter(id=project_id)[0]
    
    #downloads_obj = Downloads.objects.filter(user_id=project_obj.user_id, project_id = project_id)

    archive_size = None
    media_root = settings.MEDIA_ROOT # '/pge-nsf/media' 
    archive_path = os.path.join(media_root, 
            *['projects', project_id, 'archive.zip'])
    if os.path.isfile(archive_path):
        byte_size = os.path.getsize(archive_path)
        if byte_size > (1024*1024*100):
            archive_size = '%.2f GB' % (byte_size / float(1024*1024*1024))
        else:
            archive_size = '%.0f MB' % (byte_size / float(1024*1024))

    context = {
        'project_obj': project_obj,
        'allow_edit': project_obj.is_editable_by_user(request.user),
        #'datatable': datatable,
        'archive_size': archive_size,
        }
    return render(request, 'upload/project/view_project_rdfa.html', context)

@login_required
def project_edit_metadata(request, project_id):
    """
    Edit project metadata.

    """
    project_obj = project.objects.get(id=project_id)
    if not project_obj.is_editable_by_user(request.user):
        messages.warning(request, 'You do not have permission to edit this project.')
        return HttpResponseRedirect(reverse('view_project', args=[project_id]), status=403)

    if request.method == 'POST':
        if 'delete' in request.POST:
            project_obj.delete()
            messages.success(request, 'The project has been deleted.')
            return HttpResponseRedirect(reverse('my_projects'))
        else:
            form = ProjectEditForm(request.POST, request.FILES, instance=project_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your changes have been saved!')
                return HttpResponseRedirect(reverse('view_project', args=[project_id]))
    else:
        form = ProjectEditForm(instance=project_obj)

    context = {
        'project_obj': project_obj,
        'form': form,
        'allow_edit': True
        }
    return render(request, 'upload/project/edit_project.html', context)


def project_add_dataset(request, project_id):
    """
    Add a new dataset to the project.

    """
    project_obj = project.objects.filter(id=project_id)[0]

    if not project_obj.is_editable_by_user(request.user):
        return HttpResponse('Project is not editable', status=403)

    if request.method == 'POST':
        submission_type = request.POST.get('dataset_type')
        if submission_type == 'origin':
            origin_data_form = OriginDataForm(project_obj, request.POST)
            if origin_data_form.is_valid():
                origin_data = origin_data_form.save(commit=False)
                origin_data.project = project_obj
                origin_data.uploader = request.user
                origin_data.save()
                return HttpResponseRedirect(reverse('origin_data_summary', args=[project_obj.id, origin_data.id]))
            else:
                logger.debug(origin_data_form.errors)

            analysis_data_form = AnalysisDataForm(project_obj)
        elif submission_type == 'analysis':
            analysis_data_form = AnalysisDataForm(project_obj, request.POST)
            if analysis_data_form.is_valid():
                analysis_data = analysis_data_form.save(commit=False)
                analysis_data.project = project_obj
                analysis_data.uploader = request.user
                analysis_data.save()
                return HttpResponseRedirect(reverse('analysis_data_summary', args=[project_obj.id, analysis_data.id]))
            else:
                logger.debug(analysis_data_form.errors)

            origin_data_form = OriginDataForm(project_obj)
        else:
            messages.error(request, 'Unexpected dataset type')
    else:
        submission_type = 'origin'
        origin_data_form = OriginDataForm(project_obj)
        analysis_data_form = AnalysisDataForm(project_obj)

    context = {
        'project_obj': project_obj,
        'submission_type': submission_type,
        'origin_data_form': origin_data_form,
        'analysis_data_form': analysis_data_form,
        'allow_edit': True,
        }
    return render(request, 'upload/project/project_add_dataset.html', context)


@login_required
def dataset_image_upload(request, project_id, origin_data_id=None, analysis_data_id=None):
    project_obj = project.objects.get(pk=project_id)
    dataset = None
    dataset_type = None
    if origin_data_id:
        dataset = origin_data.objects.get(pk=origin_data_id)
        dataset_type = 'origin_data'
    elif analysis_data_id:
        dataset = analysis_data.objects.get(pk=analysis_data_id)
        dataset_type = 'analysis_data'

    if dataset is None:
        raise Exception('Missing dataset')

    if request.method == 'POST':
        form = AdvancedImageUploadForm(request.POST)
        if form.is_valid():
            df = DataFile()
            df.uploader = request.user
            if dataset_type == 'origin_data':
                df.origin_data = dataset
            else:
                df.analysis_data = dataset

            if form.cleaned_data['source'] == 'Local file':
                df.file = request.FILES.get('images')
            else:
                remote_file_url = form.cleaned_data.get('url')
                remote_file_name = form.cleaned_data.get('name')
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urllib2.urlopen(remote_file_url).read())
                img_temp.flush()
                df.file = File(img_temp, name=remote_file_name)
            # Create a task to extract and store the metadata for a file using FITS.

            if df.is_archive():
                logger.debug("Detected archive upload.")
                df.isNormalImageFile = True
                image = save_image_instance(df, request)
                process_bulk_upload.delay(image.id)
            elif df.is_advanced():
                logger.debug('Detected advanced image')
                advanced_image = form.save(commit=False)
                advanced_image.file = df.file
                advanced_image.origin_data = df.origin_data
                advanced_image.analysis_data = df.analysis_data
                advanced_image.uploader = df.uploader
                advanced_image.isAdvancedImageFile = True
                advanced_image.save()
                process_advanced_image.delay(advanced_image.id)
            else:
                logger.debug('Detected normal image')
                df.isNormalImageFile = True
                image = save_image_instance(df, request)
                make_thumbnail_image.delay(image.id)
                # histogram not supported yet...
                # extract_histogram.delay(image.id)
                extract_store_metadata.delay(image.id)

            response = {'status': 'success'}
            return JsonResponse(response)
        else:
            return JsonResponse({
                'status': 'error',
                'result': form.errors,
            }, status=400)

    else:
        context = {
            'project_obj': project_obj,
            'dataset': dataset,
            'dataset_view_url': reverse('%s_summary' % dataset_type, args=[project_obj.id, dataset.id]),
            'dropbox_app_key': settings.DROPBOX_KEY,
            'box_app_key': settings.BOX_KEY,
            'allow_edit': True,
            }
        return render(request, 'upload/project/dataset/image_upload.html', context)


@login_required
def edit_dataset_image(request, project_id, image_id):
    data_file = DataFile.objects.get(pk=image_id)
    advanced_image = getattr(data_file, 'advancedimagefile', None)

    if data_file.origin_data:
        dataset = data_file.origin_data
        dataset_url = reverse('origin_data_summary',
                              args=[dataset.project.id, dataset.id])
    else:
        dataset = data_file.analysis_data
        dataset_url = reverse('analysis_data_summary',
                              args=[dataset.project.id, dataset.id])

    if request.method == 'POST':
        if 'delete' in request.POST:
            data_file.delete()
            messages.success(request, 'Image Deleted Successfully.')
            return HttpResponseRedirect(dataset_url)

        logger.info('Saving dataset image')
        if advanced_image:
            logger.info('This is an advanced image: %s', advanced_image)
            form = AdvancedImageEditForm(request.POST, instance=advanced_image)
            if form.is_valid():
                form.save()
                logger.info('Saving advanced image: %s', str(advanced_image.id))
                process_advanced_image.delay(advanced_image.id)
                # metadata will not have changed...
                # extract_store_metadata.delay(advanced_image.id)
                messages.success(request, 'Your changes have been saved.')
                messages.info(request,
                              'Queued task to update image preview and GIF rendering.')
                return HttpResponseRedirect(dataset_url)

        else:
            logger.info('not an advanced image')
            # non-advanced images don't have anything to edit atm
            # metadata will not have changed...
            # extract_store_metadata.delay(data_file.id)
            # make_thumbnail_image.delay(data_file.id)
            return HttpResponseRedirect(dataset_url)

    elif advanced_image:
        form = AdvancedImageEditForm(instance=advanced_image)
    else:
        form = None

    context = {
        'data_file': data_file,
        'advanced_image': advanced_image,
        'dataset': dataset,
        'project_obj': dataset.project,
        'form': form,
        'dataset_url': dataset_url,
        'allow_edit': True,
    }

    return render(request, 'upload/project/dataset/edit_dataset_image.html', context)

@login_required
def add_collaborator(request, project_id):
    """
    Add a collaborator to the project.

    """
    project_obj = project.objects.get(id=project_id)

    if not project_obj.is_editable_by_user(request.user):
        return HttpResponse('Project is not editable', status=403)

    if request.POST:
        for uid in request.POST.getlist('user_id'):
            user = MyUser.objects.get(id=int(uid))
            collab = collaborator(user=user, project=project_obj)
            collab.save()
            messages.success(request, 'Added <b>%s</b> as a collaborator!' % user)

    search_q = request.GET.get('q', '')
    logger.debug('q: %s', search_q)
    if search_q:
        existing = list(collab.user.id for collab in project_obj.collaborators.all())
        existing.append(project_obj.user.id)
        results = MyUser.objects
        results = results.filter(username__icontains=search_q) | \
                    results.filter(first_name__icontains=search_q) | \
                    results.filter(last_name__icontains=search_q)

    else:
        results = None

    logger.debug('results: %s', results)
    context = {
        'project_obj': project_obj,
        'search_q': search_q,
        'results': results,
        'allow_edit': True,
    }
    return render(request, 'upload/project/add_collaborator.html', context)


FILES_PAGE_SIZE = 20


def origin_data_summary(request, project_id, origin_data_id):
    """
    This function would generate a view for the origin data
    containing its metadata and files.

    """
    # We don't need to check for authentication here. Because
    # this view would be enabled for all. However, we would
    # ensure form takes care whether user is authenticated
    # and gives required permissions.
    project_obj = project.objects.filter(id=project_id)[0]
    origin_data_obj = origin_data.objects.filter(id=origin_data_id)[0]

    paginator = Paginator(origin_data_obj.allfiles.all(), FILES_PAGE_SIZE)
    page = request.GET.get('page', 1)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    context = {
        'project_obj' : project_obj,
        'dataset' : origin_data_obj,
        'allow_edit': project_obj.is_editable_by_user(request.user),
        'images': images,
        'paginator': paginator,
    }
    return render(request, 'upload/project/dataset/origin_summary.html', context)


def analysis_data_summary(request, project_id, analysis_data_id):
    """
    This function would generate a view for the analysis data
    containing its metadata and files.

    """
    project_obj = project.objects.filter(id=project_id)[0]
    analysis_data_obj = analysis_data.objects.filter(id=analysis_data_id)[0]

    paginator = Paginator(analysis_data_obj.allfiles.all(), FILES_PAGE_SIZE)
    page = request.GET.get('page', 1)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    context = {
        'project_obj' : project_obj,
        'dataset' : analysis_data_obj,
        'allow_edit': project_obj.is_editable_by_user(request.user),
        'images': images,
        'paginator': paginator,
    }

    return render(request, 'upload/project/dataset/analysis_summary.html', context)



@login_required
def update_collab_status(request, project_id, collaborator_id):
    project_obj = project.objects.get(id=project_id)
    if not project_obj.is_editable_by_user(request.user):
        return HttpResponse('Project is not editable', status=403)

    collab = collaborator.objects.get(id=collaborator_id)
    status = request.POST.get('status')
    if request.method != 'POST' or status not in ['Collaborator', 'Author']:
        return HttpResponse('Bad Request', status=400)

    collab = collaborator.objects.get(id=collaborator_id)
    collab.status = status
    collab.save()
    logger.debug('status: %s. collab: %s. project: %s', status, collab, project_obj)

    context = {
        'project_obj': project_obj,
        'allow_edit': project_obj.is_editable_by_user(request.user),
        }
    url = reverse('project_add_collaborator', args=[project_id])
    return HttpResponseRedirect(url)

@login_required
def remove_collaborator(request, project_id, collaborator_id):
    project_obj = project.objects.get(id=project_id)
    if not project_obj.is_editable_by_user(request.user):
        return HttpResponse('Project is not editable', status=403)

    collab = collaborator.objects.get(id=collaborator_id)
    if request.POST and request.POST['confirm']:
        logger.info('Removing collaborator %s from project id=%d' % (collab.user, collab.project.id))
        collab.delete()
        messages.success(request, 'Removed <b>%s</b> from the project collaborators.' % collab)
        return HttpResponseRedirect(reverse('project_add_collaborator', args=[project_id]))

    context = {
        'collaborator': collab,
        'project_obj': project_obj,
        'allow_edit': True,
        }
    return render(request, 'upload/project/remove_collaborator.html', context)

