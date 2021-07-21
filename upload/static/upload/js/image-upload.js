/*globals jQuery*/
(function(window, $, undefined) {
'use strict';

var uploadForm = $('form[name="upload-form"]');

var tmpl = window.tmpl;
tmpl.regexp =
  /([\s'\\])(?!(?:[^<]|<(?!%))*%>)|(?:<%(=|#)([\s\S]+?)%>)|(<%)|(%>)/g;
var template = tmpl($('#template-upload').html());

var formatFileSize = function formatFileSize(bytes) {
  if (typeof bytes !== 'number') {
    return '';
  }
  if (bytes >= 1000000000) {
    return (bytes / 1000000000).toFixed(2) + ' GB';
  }
  if (bytes >= 1000000) {
    return (bytes / 1000000).toFixed(2) + ' MB';
  }
  return (bytes / 1000).toFixed(2) + ' KB';
};

var standardImageType = /(\.|\/)(gif|jpe?g|png|tiff?)$/i;
// var supportedArchiveTypes = /(\.|\/)(zipx?|ar?|tar|bz2|gz(ip)?|xz|7z|rar)$/i;
var standardZip = /(\.|\/)(zip)$/i;

var formStatus = function formStatus() {
  if ($('.files', uploadForm).children().length > 0) {
    $('.start', uploadForm).attr('disabled', false);
  } else {
    $('.start', uploadForm).attr('disabled', true);
  }
};

var removeRow = function removeRow(e) {
  e.preventDefault();
  $(this).closest('tr').remove();
  formStatus();
};

var processCloudUpload = function processCloudUpload(files) {
  $.each(files, function(i, file) {
    file.standardImage = standardImageType.test(file.name);
    file.sizeFmt = formatFileSize(file.size);
    $(template({
        file: file
      }))
      .appendTo('.files', uploadForm)
      .addClass('in')
      .find('.cancel').on('click', removeRow);
  });
  formStatus();
};

var processLocalUpload = function processLocalUpload(data) {
  if (data.files.length > 0) {
    /* hold on to data for later submission */
    var uploads = uploadForm.data('uploads') || [];
    uploads.push(data);
    uploadForm.data('uploads', uploads);

    /* template form row */
    var file = data.files[0];
    var oFile = {
      name: file.name,
      size: file.size,
      sizeFmt: formatFileSize(file.size),
      source: 'Local file',
      standardImage: standardImageType.test(file.name) &&
        standardImageType.test(file.type),
      isArchive: standardZip.test(file.name)
    };

    var finish = function finish() {
      var row = $(template({
        file: oFile
      }));
      row.find('[name="images.file"]').val(file);
      row.appendTo('.files', uploadForm)
        .addClass('in')
        .find('.cancel').on('click', function(e) {
          uploads.splice(uploads.indexOf(data), 1);
          removeRow.bind(this)(e);
        });
      data.context = row;
      formStatus();
    };

    if (standardZip.test(file.type)) {
      var zip = new JSZip();
      zip.loadAsync(file)
        .then(function(zip) {
              for (var item in zip.files) {
                if (standardImageType.test(item)) {
                  oFile.standardImage = true;
                  break;
                }
              }
              finish();
            },
            function() {
              finish();
            }
        );
    } else {
      finish();
    }
  }
};


var blockUI = function(context) {
  $('.upload-options .btn', context).addClass('disabled').attr('disabled', true);
  $('.upload-options input[name="images"]', context).attr('disabled', true);
  $('.upload-progress', context).addClass('show');
  $('.actions button, .actions a', context).attr('disabled', true).addClass('disabled');
};

var uploadFinished = function(context) {
  $('.upload-progress .progress-bar', context).addClass('progress-bar-success');
  $('.actions button', context).addClass('hide');
  $('.actions a', context).attr('disabled', null).removeClass('disabled btn-link').addClass('btn-lg btn-default');
  $('.actions', context).append('<a href="javascript:window.location.reload()" class="btn btn-link">Upload more data</a>');
};

uploadForm.fileupload({
  add: function(e, data) {
    processLocalUpload(data);
  },
  done: function(e, data) {
    data.context.addClass('success').html('<td colspan="3">Upload complete.</td>');
  },
  fail: function(e, data) {
    data.context.addClass('danger');
  },
  progressall: function(e, data) {
    var progress = parseInt(data.loaded / data.total * 100, 10);
    $('.progress-bar')
      .css('width', progress + '%')
      .attr('aria-valuenow', progress)
      .html('<span class="sr-only">' + progress + '% Complete</span>');
  }
});



/* actual submit handler */
uploadForm.on('submit', function(e) {
  e.preventDefault();

  var self = this;

  /* block UI */
  blockUI(this);

  // TODO validate additional data
  // TODO handle errors?
  // TODO promises?

  /* queue cloud uploads */
  var tasks = [];
  $('.cloud-upload').each(function(i, cloudUpload) {
    var data = $(':input', cloudUpload).serializeArray();
    var xhr = $.ajax({
      context: cloudUpload,
      data: data,
      dataType: 'json',
      method: 'POST'
    })
    .done(function(data, status, xhr) {
      $(this).addClass('success').html('<td colspan="3">Cloud upload request queued.</td>');
    })
    .fail(function(xhr, status, error) {
      $(this).addClass('danger');
      console.error(status);
      console.error(error);
    });
    tasks.push(xhr.promise());
  });

  /* upload local files */
  var uploads = uploadForm.data('uploads');
  $('.local-upload').each(function(i, localUpload) {
    var formData = $(':input', localUpload).serializeArray();
    var upload = uploads[i];
    upload.formData = formData;
    var xhr = upload.submit();
    tasks.push(xhr.promise());
  });

  $.when.apply($, tasks).done(function() {
    uploadFinished(self);
  });
});

/* Dropbox */
if (window.Dropbox) {
  $('.btn-dropbox').on('click', function(e) {
    var dropboxOptions = {
      success: function(files) {
        processCloudUpload($.map(files, function(f) {
          return {
            source: 'Dropbox',
            name: f.name,
            url: f.link,
            size: f.bytes
          };
        }));
      },
      linkType: "direct",
      multiselect: true
    };
    Dropbox.choose(dropboxOptions);
  });
} else {
  console.warn('Dropbox unavailable!');
  $('.btn-dropbox').attr('disabled', 'disabled');
}

/* Box */
if (window.BoxSelect) {
  var boxSelect = new window.BoxSelect();
  boxSelect.success(function(files) {
    processCloudUpload($.map(files, function(f) {
      return {
        source: 'Box.com',
        name: f.name,
        url: f.url,
        size: f.size
      };
    }));
  });
  $('.btn-box').on('click', function(e) {
    e.preventDefault();
    boxSelect.launchPopup();
  });
} else {
  console.warn('BoxSelect unavailable!');
  $('.btn-box').attr('disabled', 'disabled');
}

})(window, jQuery);
