(function(window, $, undefined) {

    var jobStatusEl = $('.jobstatus');
    var jobId = jobStatusEl.data('jobid');
    var checkText = jobStatusEl.data('checktext');

    function checkJobStatus() {
        jobStatusEl.text(checkText);
        $.ajax({
            url: '/projects/job_queued/',
            data: {job_id: jobId},
            success: function(resp) {
                jobStatusEl.text(resp.status + '...');
                if (resp.status === 'RUNNING' && resp.host) {
                    var query = [];
                    query.push('hostname='+resp.host);
                    query.push('port='+resp.port);
                    query.push('autoconnect=true');
                    query.push('password='+resp.password);

                    var link = $('<a class="btn btn-primary btn-lg" target="_blank">');
                    link.text('Connect to Remote Job');
                    link.attr('href', 'https://vis.tacc.utexas.edu/no-vnc/vnc.html?'+query.join('&'));
                    // https://vis.tacc.utexas.edu/no-vnc/vnc.html?hostname=vis.tacc.utexas.edu&port=51281&autoconnect=true&password=7365227830803436006-242ac115-0001-007

                    jobStatusEl.parent().append(link);
                } else {
                    setTimeout(checkJobStatus, 1000);
                }
            }
        });
    }

    checkJobStatus();
})(window, jQuery);
