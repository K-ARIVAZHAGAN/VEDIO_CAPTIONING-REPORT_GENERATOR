/**
 * Video Captioning - Clean Google-Style UI
 */

let uploadedFilePath = null;
let currentJobId = null;
let statusInterval = null;
let currentJsonPath = null;
let currentSessionDir = null;

console.log('app.js loaded - jQuery available:', typeof $ !== 'undefined');

$(document).ready(function() {
    console.log('DOM ready - initializing handlers');
    initHandlers();
    loadGooglePicker();
});

var googleAccessToken = null;
var tokenClient = null;

function loadGooglePicker() {
    if (GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== '' && GOOGLE_API_KEY && GOOGLE_API_KEY !== '') {
        // Initialize the Google Identity Services token client
        tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            scope: 'https://www.googleapis.com/auth/drive.readonly',
            callback: (tokenResponse) => {
                googleAccessToken = tokenResponse.access_token;
                console.log('Access token received');
            },
        });
        
        // Load the picker API
        gapi.load('picker', () => {
            console.log('Google Picker API loaded successfully');
        });
        
        console.log('Google Identity Services initialized');
    } else {
        console.warn('Google Drive not configured - missing Client ID or API Key');
    }
}

function initHandlers() {
    console.log('initHandlers called - binding events');
    console.log('urlInput element found:', $('#urlInput').length);
    
    // URL Input - handle Enter key
    $('#urlInput').on('keydown', function(e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            e.preventDefault();
            e.stopPropagation();
            const url = $(this).val().trim();
            console.log('Enter key pressed, URL:', url);
            if (url) {
                handleUrlInput(url);
            }
        }
    });
    
    // YouTube input paste or change detection
    $('#youtubeUrlInput').on('input paste', function() {
        setTimeout(() => {
            const url = $(this).val().trim();
            console.log('YouTube input changed, URL:', url);
            if (url && (url.includes('youtube.com') || url.includes('youtu.be') || url.startsWith('http'))) {
                console.log('Valid URL detected, calling handleUrlInput');
                handleUrlInput(url);
            }
        }, 100);
    });
    
    // YouTube input Enter key (optional - also works with Enter)
    $('#youtubeUrlInput').on('keydown', function(e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            e.preventDefault();
            const url = $(this).val().trim();
            if (url) {
                console.log('Enter pressed, calling handleUrlInput');
                handleUrlInput(url);
            }
        }
    });
    
    // Upload from computer
    $('#uploadFileBtn').click(function() {
        $('#fileInput').click();
    });
    
    // Google Drive picker
    $('#googleDriveBtn').click(function() {
        openGoogleDrivePicker();
    });
    
    // Dropbox chooser
    $('#dropboxBtn').click(function() {
        openDropboxChooser();
    });
    
    // File input
    $('#fileInput').change(function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
    
    // Remove file/URL
    $('#removeFile').click(function() {
        clearFile();
    });
    
    // Process button
    $('#processBtn').click(function() {
        processVideo();
    });
    
    // Process again
    $('#processAgain').click(function() {
        resetAll();
    });
    
    // Report tabs
    $(document).on('click', '.report-tab', function() {
        const reportType = $(this).data('report');
        $('.report-tab').removeClass('active');
        $(this).addClass('active');
        $('.report-panel').removeClass('active');
        $('#report' + reportType.charAt(0).toUpperCase() + reportType.slice(1)).addClass('active');
    });
    
    // Download video
    $(document).on('click', '#downloadVideo', function() {
        const videoSrc = $('#videoPlayer').attr('src');
        if (videoSrc) {
            const downloadUrl = videoSrc.replace('attachment=false', 'attachment=true');
            window.location.href = downloadUrl;
        }
    });
}

function handleUrlInput(url) {
    console.log('handleUrlInput called with:', url);
    
    // Add https:// if missing
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }
    
    // Set the uploaded file path
    uploadedFilePath = url;
    console.log('uploadedFilePath set to:', uploadedFilePath);
    
    // Determine icon based on URL
    let icon = '<i class="fas fa-link"></i>';
    let label = 'Video URL';
    
    if (url.toLowerCase().includes('youtube.com') || url.toLowerCase().includes('youtu.be')) {
        icon = '<i class="fab fa-youtube" style="color: #ff0000;"></i>';
        label = 'YouTube Video';
    } else if (url.toLowerCase().includes('drive.google.com')) {
        icon = '<i class="fab fa-google-drive" style="color: #4285f4;"></i>';
        label = 'Google Drive Video';
    } else if (url.toLowerCase().includes('dropbox.com')) {
        icon = '<i class="fab fa-dropbox" style="color: #0061ff;"></i>';
        label = 'Dropbox Video';
    }
    
    // Show file info
    $('#fileInfo').show();
    $('#fileName').html(icon + ' ' + label);
    $('#urlInput').val('');
    
    console.log('File info displayed, uploadedFilePath:', uploadedFilePath);
}

function openGoogleDrivePicker() {
    if (!GOOGLE_CLIENT_ID || GOOGLE_CLIENT_ID === '') {
        alert('Google Drive not configured. Please add credentials to .env file.');
        return;
    }
    
    if (typeof google === 'undefined' || !google.picker) {
        alert('Google Picker API not loaded. Please refresh the page.');
        return;
    }
    
    if (!tokenClient) {
        alert('Google Identity Services not initialized. Please refresh the page.');
        return;
    }
    
    // Request access token and show picker when received
    tokenClient.callback = async (response) => {
        if (response.error !== undefined) {
            console.error('Token error:', response);
            alert('Failed to authenticate with Google Drive');
            return;
        }
        googleAccessToken = response.access_token;
        showPicker();
    };
    
    // Check if we already have a valid token
    if (googleAccessToken) {
        showPicker();
    } else {
        // Request a new token
        tokenClient.requestAccessToken({ prompt: 'select_account' });
    }
}

function showPicker() {
    const picker = new google.picker.PickerBuilder()
        .addView(google.picker.ViewId.DOCS_VIDEOS)
        .setOAuthToken(googleAccessToken)
        .setDeveloperKey(GOOGLE_API_KEY)
        .setCallback(pickerCallback)
        .setOrigin(window.location.protocol + '//' + window.location.host)
        .build();
    picker.setVisible(true);
}

function pickerCallback(data) {
    if (data.action === google.picker.Action.PICKED) {
        const file = data.docs[0];
        const fileId = file.id;
        const fileName = file.name;
        
        // Show file selected
        uploadedFilePath = `https://drive.google.com/file/d/${fileId}/view`;
        $('#fileInfo').show();
        $('#fileName').html('<i class="fab fa-google-drive" style="color: #4285f4;"></i> ' + fileName);
    }
}

function openDropboxChooser() {
    if (!DROPBOX_APP_KEY || DROPBOX_APP_KEY === '') {
        alert('Dropbox not configured. Please configure in .env file.');
        return;
    }
    
    Dropbox.choose({
        success: function(files) {
            const file = files[0];
            // Use direct download link by changing dl=0 to dl=1
            let fileLink = file.link;
            if (fileLink.includes('dl=0')) {
                fileLink = fileLink.replace('dl=0', 'dl=1');
            } else if (!fileLink.includes('dl=')) {
                fileLink += (fileLink.includes('?') ? '&' : '?') + 'dl=1';
            }
            uploadedFilePath = fileLink;
            console.log('Dropbox file selected:', fileLink);
            $('#fileInfo').show();
            $('#fileName').html('<i class="fab fa-dropbox" style="color: #0061ff;"></i> ' + file.name);
        },
        linkType: "direct",
        multiselect: false,
        extensions: ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    });
}

function handleFile(file) {
    if (!file.type.startsWith('video/')) {
        alert('Please select a video file');
        return;
    }
    
    // Show file info
    $('#fileInfo').show();
    $('#fileName').html('<i class="fas fa-spinner fa-spin"></i> Uploading ' + file.name + '...');
    
    // Upload file
    const formData = new FormData();
    formData.append('file', file);
    
    $.ajax({
        url: '/api/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            uploadedFilePath = response.filepath;
            $('#fileName').html('<i class="fas fa-check-circle" style="color: #34a853;"></i> ' + file.name);
        },
        error: function() {
            alert('Upload failed');
            clearFile();
        }
    });
}

function clearFile() {
    uploadedFilePath = null;
    $('#fileInput').val('');
    $('#urlInput').val('');
    $('#fileInfo').hide();
    console.log('clearFile called - uploadedFilePath reset to null');
}

function processVideo() {
    console.log('processVideo called, uploadedFilePath:', uploadedFilePath);
    
    // Get video source
    let videoSource = uploadedFilePath;
    let isUrl = false;
    
    if (!videoSource) {
        console.error('No video source available');
        alert('Please upload a video or select from cloud storage');
        return;
    }
    
    console.log('Processing video source:', videoSource);
    
    // Check if it's a URL (starts with http:// or https://)
    if (videoSource.startsWith('http://') || videoSource.startsWith('https://')) {
        isUrl = true;
        console.log('Detected as URL');
    } else {
        console.log('Detected as local file path');
    }
    
    // Get model
    const modelSize = $('#modelSize').val();
    
    // Generate session name for tracking
    const now = new Date();
    const sessionName = `session_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}`;
    
    // Determine initial progress message based on source
    let initialMessage = 'Processing...';
    if (isUrl) {
        if (videoSource.includes('youtube.com') || videoSource.includes('youtu.be')) {
            initialMessage = 'Downloading from YouTube...';
        } else if (videoSource.includes('drive.google.com')) {
            initialMessage = 'Downloading from Google Drive...';
        } else if (videoSource.includes('dropbox.com')) {
            initialMessage = 'Downloading from Dropbox...';
        } else {
            initialMessage = 'Downloading from cloud storage...';
        }
    }
    
    // Show progress card with download message
    showProgress();
    $('#progressText').text(initialMessage);
    
    // Start processing
    $.ajax({
        url: '/api/process',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            video_source: videoSource,
            is_url: isUrl,
            model_size: modelSize,
            session_name: sessionName
        }),
        success: function(response) {
            currentJobId = response.job_id;
            checkStatus();
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Failed to start processing';
            alert('Error: ' + errorMsg);
        }
    });
}

function showProgress() {
    $('#mainCard').hide();
    $('#resultsCard').hide();
    $('#progressCard').show();
    $('#progressBar').css('width', '0%');
    $('#progressPercent').text('0%');
    $('#progressText').text('Processing...');
}

function checkStatus() {
    if (!currentJobId) return;
    
    statusInterval = setInterval(function() {
        $.ajax({
            url: `/api/status/${currentJobId}`,
            type: 'GET',
            success: function(status) {
                const progress = Math.round(status.progress);
                $('#progressBar').css('width', progress + '%');
                $('#progressPercent').text(progress + '%');
                
                // Update message - keep download message visible until progress reaches 10%
                if (progress >= 10 || !status.message.includes('Starting')) {
                    $('#progressText').text(status.message);
                }
                
                if (status.status === 'completed') {
                    clearInterval(statusInterval);
                    showResults(status.result);
                } else if (status.status === 'failed') {
                    clearInterval(statusInterval);
                    alert('Processing failed: ' + status.message);
                    resetAll();
                }
            },
            error: function() {
                clearInterval(statusInterval);
                alert('Failed to check status');
                resetAll();
            }
        });
    }, 2000);
}

function showResults(result) {
    $('#progressCard').hide();
    $('#resultsCard').show();
    
    // Format helpers
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}m ${secs}s`;
    };
    
    const formatDate = () => {
        return new Date().toLocaleString('en-US', {
            month: 'numeric',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            second: 'numeric'
        });
    };
    
    // Show video player if video output exists
    if (result.video_output) {
        $('#videoPlayerSection').show();
        const videoUrl = `/api/download/${encodeURIComponent(result.video_output)}?attachment=false`;
        $('#videoPlayer').attr('src', videoUrl);
        
        // Captions are burned into the video, no separate track needed
    } else {
        $('#videoPlayerSection').hide();
    }
    
    // Build summary HTML
    const summaryHTML = `
        <div style="padding: 20px;">
            <h3 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 500;">Processing Summary</h3>
            <div style="border-bottom: 1px solid #dadce0; margin-bottom: 16px;"></div>
            
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 500; color: #5f6368;">Video Information:</h4>
                <div style="font-size: 14px; line-height: 1.8;">
                    <div>• Duration: ${formatDuration(result.duration)}</div>
                    <div>• Scenes Detected: ${result.scenes_count}</div>
                    <div>• Processing Time: ${formatDuration(result.processing_time)}</div>
                </div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 500; color: #5f6368;">Output Files:</h4>
                <div style="font-size: 14px; line-height: 1.8;">
                    <div>• Video with Captions: ${result.video_output ? '✓' : '✗'}</div>
                    <div>• SRT Captions: ${result.caption_file ? '✓' : '✗'}</div>
                    <div>• Report: Available (PDF/DOCX/TXT)</div>
                </div>
            </div>
            
            <div style="font-size: 12px; color: #5f6368; margin-top: 16px; padding-top: 16px; border-top: 1px solid #dadce0;">
                Generated: ${formatDate()}
            </div>
        </div>
    `;
    
    // Populate summary panel
    $('#reportSummary').html(summaryHTML);
    
    // Remove the separate report download button since it's now in Downloads section
    $('#reportDownloadBtn').html('');
    
    // Show report viewer
    $('#reportViewerSection').show();
    
    // Load transcript and timeline data
    if (result.transcript_file || result.report_files.length > 0) {
        loadReportData(result);
    }
    
    // Build download list (video, captions, and report)
    let html = '';
    
    if (result.video_output) {
        html += createResultItem('Video with Captions', result.video_output, 'fa-file-video');
    }
    
    if (result.caption_file) {
        html += createResultItem('SRT Captions', result.caption_file, 'fa-closed-captioning');
    }
    
    // Add report download button in same style
    html += `
        <div class="result-item">
            <div class="result-item-info">
                <i class="fas fa-file-pdf"></i>
                <strong>Report (PDF/DOCX/TXT)</strong>
            </div>
            <button class="btn-download-report" style="background: #1a73e8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 500; font-size: 14px;">
                <i class="fas fa-download"></i> Download
            </button>
        </div>
    `;
    
    // Store JSON path and session dir for report conversion
    currentSessionDir = result.session_dir;
    if (result.report_files) {
        result.report_files.forEach(file => {
            const ext = file.split('.').pop().toUpperCase();
            if (ext === 'JSON') {
                currentJsonPath = file;
            }
        });
    }
    
    $('#resultsList').html(html);
    
    // Download handlers
    $('.btn-download').click(function() {
        const filepath = $(this).data('file');
        window.location.href = `/api/download/${encodeURIComponent(filepath)}?attachment=true`;
    });
    
    // Report download handler - show format selector
    $(document).off('click', '.btn-download-report');
    $(document).on('click', '.btn-download-report', function() {
        showFormatSelector();
    });
}

function loadReportData(result) {
    // Load transcript
    if (result.transcript_file) {
        $.get(`/api/transcript/${encodeURIComponent(result.transcript_file)}`, function(data) {
            $('#reportTranscript').text(data);
        }).fail(function(xhr) {
            console.error('Failed to load transcript:', xhr);
            $('#reportTranscript').html('<p style="color: #5f6368;">Transcript not available</p>');
        });
    } else {
        $('#reportTranscript').html('<p style="color: #5f6368;">Transcript not generated</p>');
    }
    
    // Load caption file for timeline
    if (result.caption_file) {
        $.get(`/api/captions/${encodeURIComponent(result.caption_file)}`, function(data) {
            const timeline = parseSRT(data);
            displayTimeline(timeline);
        }).fail(function(xhr) {
            console.error('Failed to load captions:', xhr);
            $('#reportTimeline').html('<p style="color: #5f6368;">Timeline not available</p>');
        });
    } else {
        $('#reportTimeline').html('<p style="color: #5f6368;">Captions not generated</p>');
    }
    
    // Load JSON report for scenes and AI summary
    if (result.report_files && result.report_files.length > 0) {
        const jsonReport = result.report_files.find(f => f.endsWith('report.json'));
        if (jsonReport) {
            $.getJSON(`/api/download/${encodeURIComponent(jsonReport)}?attachment=false`, function(reportData) {
                displayScenes(reportData.scenes || [], result.session_dir);
                
                // Load AI summary if available
                loadAISummary(result.session_dir);
            }).fail(function(xhr) {
                console.error('Failed to load report JSON:', xhr);
                $('#reportScenes').html('<p style="color: #5f6368;">Scenes data not available</p>');
            });
        }
    }
    
    // Generate summary
    const summary = `
Processing Summary:
═══════════════════════════════════════

Video Information:
• Duration: ${formatDuration(result.duration)}
• Scenes Detected: ${result.scenes_count || 0}
• Processing Time: ${formatDuration(result.processing_time)}

Output Files:
• Video with Captions: ${result.video_output ? '✓' : '✗'}
• SRT Captions: ${result.caption_file ? '✓' : '✗'}
• Report: Available (PDF/DOCX/TXT)

Generated: ${new Date().toLocaleString()}
    `;
    
    $('#reportSummary').text(summary);
}

function parseSRT(srtContent) {
    const timeline = [];
    const blocks = srtContent.trim().split('\n\n');
    
    blocks.forEach(block => {
        const lines = block.split('\n');
        if (lines.length >= 3) {
            const timecode = lines[1];
            const text = lines.slice(2).join(' ');
            const startTime = timecode.split(' --> ')[0];
            const seconds = srtTimeToSeconds(startTime);
            timeline.push({ time: startTime, seconds: seconds, text: text });
        }
    });
    
    return timeline;
}

function srtTimeToSeconds(timeString) {
    // Convert SRT time format (HH:MM:SS,mmm) to seconds
    const parts = timeString.replace(',', '.').split(':');
    const hours = parseInt(parts[0]) || 0;
    const minutes = parseInt(parts[1]) || 0;
    const seconds = parseFloat(parts[2]) || 0;
    return hours * 3600 + minutes * 60 + seconds;
}

function displayScenes(scenes) {
    if (!scenes || scenes.length === 0) {
        $('#reportScenes').html('<p style="color: #5f6368;">No scenes detected</p>');
        return;
    }
    
    let html = '<div style="padding: 20px;"><h4 style="margin: 0 0 20px 0; color: #202124;">Visual Timeline - ' + scenes.length + ' Scenes Detected</h4>';
    html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">';
    
    scenes.forEach(scene => {
        const duration = scene.end_time ? (scene.end_time - scene.start_time).toFixed(1) : 'N/A';
        const framePath = scene.frame_path ? scene.frame_path.replace(/\\/g, '/').split('/frames/')[1] : null;
        const frameUrl = framePath ? `/api/download/frames/${encodeURIComponent(framePath)}?attachment=false` : null;
        
        html += `
            <div class="scene-card" style="border: 1px solid #dadce0; border-radius: 8px; overflow: hidden; background: white; transition: box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" onmouseout="this.style.boxShadow='none'">
                ${frameUrl ? `
                    <div style="position: relative; cursor: pointer;" class="scene-frame" data-time="${scene.start_time}">
                        <img src="${frameUrl}" alt="Scene ${scene.scene_number}" style="width: 100%; height: 200px; object-fit: cover; display: block;" onerror="this.parentElement.innerHTML='<div style=\"height:200px;display:flex;align-items:center;justify-content:center;background:#f8f9fa;color:#5f6368;\"><i class=\"fas fa-image\" style=\"font-size:48px;\"></i></div>'">
                        <div style="position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            <i class="fas fa-play-circle"></i> ${formatTime(scene.start_time)}
                        </div>
                    </div>
                ` : '<div style="height: 200px; display: flex; align-items: center; justify-content: center; background: #f8f9fa; color: #5f6368;"><i class="fas fa-image" style="font-size: 48px;"></i></div>'}
                <div style="padding: 16px;">
                    <div style="font-weight: 500; color: #202124; margin-bottom: 8px;">Scene ${scene.scene_number}</div>
                    <div style="font-size: 13px; color: #5f6368; line-height: 1.6;">
                        <div><i class="fas fa-clock" style="width: 16px;"></i> ${formatTime(scene.start_time)} - ${scene.end_time ? formatTime(scene.end_time) : 'End'}</div>
                        <div><i class="fas fa-hourglass-half" style="width: 16px;"></i> Duration: ${duration}s</div>
                    </div>
                    ${scene.description ? `<div style="margin-top: 12px; font-size: 13px; color: #202124; padding-top: 12px; border-top: 1px solid #f1f3f4;">${scene.description}</div>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div></div>';
    $('#reportScenes').html(html);
    
    // Add click handlers to jump to scene in video
    $('.scene-frame').click(function() {
        const time = parseFloat($(this).data('time'));
        const videoPlayer = document.getElementById('videoPlayer');
        
        if (videoPlayer && !isNaN(time)) {
            videoPlayer.currentTime = time;
            videoPlayer.play();
            
            // Scroll to video player and highlight
            $('#videoPlayerSection')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Visual feedback
            $(this).css('opacity', '0.7');
            setTimeout(() => {
                $(this).css('opacity', '1');
            }, 300);
        }
    });
}

function displayScenes(scenes, sessionDir) {
    if (!scenes || scenes.length === 0) {
        $('#reportScenes').html('<p style="color: #5f6368;">No scenes detected</p>');
        return;
    }
    
    const container = $('<div style="padding: 20px;"></div>');
    const title = $('<h4 style="margin: 0 0 20px 0; color: #202124;"><i class="fas fa-film"></i> Visual Timeline - ' + scenes.length + ' Scenes Detected</h4>');
    const grid = $('<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;"></div>');
    
    scenes.forEach(scene => {
        const duration = scene.end_time ? (scene.end_time - scene.start_time).toFixed(1) : 'N/A';
        const frameUrl = scene.frame_path ? `/api/download/${encodeURIComponent(scene.frame_path)}?attachment=false` : null;
        
        const card = $('<div class="scene-card"></div>').css({
            'border': '1px solid #dadce0',
            'border-radius': '8px',
            'overflow': 'hidden',
            'background': 'white',
            'transition': 'box-shadow 0.2s',
            'cursor': 'pointer'
        }).hover(
            function() { $(this).css('box-shadow', '0 4px 12px rgba(0,0,0,0.1)'); },
            function() { $(this).css('box-shadow', 'none'); }
        ).click(function() { jumpToScene(scene.start_time); });
        
        if (frameUrl) {
            const imgContainer = $('<div style="position: relative;"></div>');
            const img = $('<img>').attr({
                'src': frameUrl,
                'alt': 'Scene ' + scene.scene_number
            }).css({
                'width': '100%',
                'height': '200px',
                'object-fit': 'cover',
                'display': 'block'
            }).on('error', function() {
                $(this).parent().html('<div style="height:200px;display:flex;align-items:center;justify-content:center;background:#f8f9fa;color:#5f6368;"><i class="fas fa-image" style="font-size:48px;"></i></div>');
            });
            
            const badge = $('<div></div>').css({
                'position': 'absolute',
                'top': '8px',
                'right': '8px',
                'background': 'rgba(0,0,0,0.7)',
                'color': 'white',
                'padding': '4px 8px',
                'border-radius': '4px',
                'font-size': '12px'
            }).html('<i class="fas fa-play-circle"></i> ' + formatTime(scene.start_time));
            
            imgContainer.append(img).append(badge);
            card.append(imgContainer);
        } else {
            card.append('<div style="height: 200px; display: flex; align-items: center; justify-content: center; background: #f8f9fa; color: #5f6368;"><i class="fas fa-image" style="font-size: 48px;"></i></div>');
        }
        
        const info = $('<div style="padding: 16px;"></div>');
        info.append('<div style="font-weight: 500; color: #202124; margin-bottom: 8px;">Scene ' + scene.scene_number + '</div>');
        
        const details = $('<div style="font-size: 13px; color: #5f6368; line-height: 1.6;"></div>');
        details.append('<div><i class="fas fa-clock" style="width: 16px;"></i> ' + formatTime(scene.start_time) + ' - ' + (scene.end_time ? formatTime(scene.end_time) : 'End') + '</div>');
        details.append('<div><i class="fas fa-hourglass-half" style="width: 16px;"></i> Duration: ' + duration + 's</div>');
        info.append(details);
        
        if (scene.description) {
            info.append('<div style="margin-top: 12px; font-size: 13px; color: #202124; padding-top: 12px; border-top: 1px solid #f1f3f4;">' + scene.description + '</div>');
        }
        
        card.append(info);
        grid.append(card);
    });
    
    container.append(title).append(grid);
    $('#reportScenes').html('').append(container);
}

function jumpToScene(time) {
    const videoPlayer = document.getElementById('videoPlayer');
    
    if (videoPlayer && !isNaN(time)) {
        videoPlayer.currentTime = time;
        videoPlayer.play();
        
        // Scroll to video player
        $('#videoPlayerSection')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function displayTimeline(timeline) {
    let html = '';
    timeline.forEach(item => {
        html += `
            <div class="timeline-item">
                <div class="timeline-time clickable-time" data-seconds="${item.seconds}" title="Click to jump to ${item.time}">${item.time}</div>
                <div class="timeline-text">${item.text}</div>
            </div>
        `;
    });
    $('#reportTimeline').html(html || '<p style="color: #5f6368;">No timeline data available</p>');
    
    // Add click handlers for timeline timestamps
    $('.clickable-time').click(function() {
        const seconds = parseFloat($(this).data('seconds'));
        const videoPlayer = document.getElementById('videoPlayer');
        
        if (videoPlayer && !isNaN(seconds)) {
            videoPlayer.currentTime = seconds;
            videoPlayer.play();
            
            // Scroll to video player
            $('#videoPlayerSection')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Visual feedback
            $(this).css('background-color', '#e8f0fe');
            setTimeout(() => {
                $(this).css('background-color', '');
            }, 500);
        }
    });
}

function formatDuration(seconds) {
    if (!seconds) return '0s';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function createResultItem(name, filepath, icon) {
    return `
        <div class="result-item">
            <div class="result-item-info">
                <i class="fas ${icon}"></i>
                <strong>${name}</strong>
            </div>
            <button class="btn-download" data-file="${filepath}">
                <i class="fas fa-download"></i> Download
            </button>
        </div>
    `;
}

function addDownloadLink(filename, displayName) {
    const ext = filename.split('.').pop().toUpperCase();
    const icon = ext === 'PDF' ? 'fa-file-pdf' : 
                 ext === 'DOCX' ? 'fa-file-word' : 
                 ext === 'TXT' ? 'fa-file-alt' : 'fa-file';
    
    const html = createResultItem(displayName, filename, icon);
    $('#resultsList').append(html);
    
    // Rebind download handlers
    $('.btn-download').off('click').click(function() {
        const filepath = $(this).data('file');
        window.location.href = `/api/download/${encodeURIComponent(filepath)}?attachment=true`;
    });
}

// Show format selector modal
function showFormatSelector() {
    const modal = `
        <div id="formatModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); max-width: 400px; width: 90%;">
                <h3 style="margin: 0 0 20px 0; color: #202124;">Select Report Format</h3>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button class="format-option" data-format="pdf" style="padding: 16px; border: 2px solid #dadce0; border-radius: 8px; background: white; cursor: pointer; text-align: left; transition: all 0.2s;">
                        <i class="fas fa-file-pdf" style="color: #ea4335; font-size: 20px; margin-right: 12px;"></i>
                        <span style="font-weight: 500;">PDF Document</span>
                    </button>
                    <button class="format-option" data-format="docx" style="padding: 16px; border: 2px solid #dadce0; border-radius: 8px; background: white; cursor: pointer; text-align: left; transition: all 0.2s;">
                        <i class="fas fa-file-word" style="color: #4285f4; font-size: 20px; margin-right: 12px;"></i>
                        <span style="font-weight: 500;">Word Document</span>
                    </button>
                    <button class="format-option" data-format="txt" style="padding: 16px; border: 2px solid #dadce0; border-radius: 8px; background: white; cursor: pointer; text-align: left; transition: all 0.2s;">
                        <i class="fas fa-file-alt" style="color: #34a853; font-size: 20px; margin-right: 12px;"></i>
                        <span style="font-weight: 500;">Text File</span>
                    </button>
                </div>
                <div style="margin-top: 20px; padding: 16px; background: #f8f9fa; border-radius: 8px;">
                    <label style="display: flex; align-items: center; cursor: pointer;">
                        <input type="checkbox" id="includeAISummary" checked style="width: 18px; height: 18px; margin-right: 12px; cursor: pointer;">
                        <span style="color: #202124; font-weight: 500;"><i class="fas fa-robot" style="color: #1a73e8; margin-right: 8px;"></i>Include AI Summary</span>
                    </label>
                    <p style="margin: 8px 0 0 30px; font-size: 12px; color: #5f6368;">Add AI-generated summary and key points to the report</p>
                </div>
                <button id="closeModal" style="margin-top: 20px; width: 100%; padding: 12px; border: 1px solid #dadce0; border-radius: 4px; background: white; cursor: pointer; font-weight: 500;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    $('body').append(modal);
    
    // Hover effects
    $('.format-option').hover(
        function() { $(this).css({'border-color': '#1a73e8', 'background': '#f1f3f4'}); },
        function() { $(this).css({'border-color': '#dadce0', 'background': 'white'}); }
    );
    
    // Format selection
    $('.format-option').click(function() {
        const format = $(this).data('format');
        const includeAI = $('#includeAISummary').is(':checked');
        $('#formatModal').remove();
        downloadReport(format, includeAI);
    });
    
    // Close modal
    $('#closeModal, #formatModal').click(function(e) {
        if (e.target === this) {
            $('#formatModal').remove();
        }
    });
}

async function downloadReport(format, includeAI = true) {
    if (!currentJsonPath) {
        alert('No report available');
        return;
    }
    
    try {
        // Show loading indicator
        $('body').append('<div id="loadingOverlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 2000;"><div style="background: white; padding: 30px; border-radius: 12px; text-align: center;"><i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #1a73e8; margin-bottom: 12px;"></i><div style="color: #202124; font-weight: 500;">Generating ' + format.toUpperCase() + '...</div></div></div>');
        
        // Fetch the JSON report
        const response = await fetch(`/api/download/${encodeURIComponent(currentJsonPath)}`);
        if (!response.ok) throw new Error('Failed to load report');
        
        const reportData = await response.json();
        
        // Load AI summary if we need to include it
        if (includeAI && currentSessionDir) {
            try {
                const aiSummaryPath = currentSessionDir + '/reports/ai_summary.json';
                const aiResponse = await fetch(`/api/download/${encodeURIComponent(aiSummaryPath)}?attachment=false`);
                if (aiResponse.ok) {
                    reportData.ai_summary = await aiResponse.json();
                }
            } catch (e) {
                console.log('AI summary not available:', e);
            }
        }
        
        const baseFilename = 'report_' + new Date().getTime();
        
        if (format === 'pdf') {
            const doc = generatePDF(reportData, includeAI);
            doc.save(`${baseFilename}.pdf`);
        } else if (format === 'docx') {
            const docContent = generateDOCX(reportData);
            const zip = new PizZip();
            zip.file('word/document.xml', docContent);
            zip.file('[Content_Types].xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>`);
            zip.file('_rels/.rels', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>`);
            const blob = zip.generate({ type: 'blob', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
            saveAs(blob, `${baseFilename}.docx`);
        } else if (format === 'txt') {
            const text = generateTXT(reportData, includeAI);
            const blob = new Blob([text], { type: 'text/plain' });
            saveAs(blob, `${baseFilename}.txt`);
        }
        
        $('#loadingOverlay').remove();
    } catch (error) {
        $('#loadingOverlay').remove();
        console.error('Download error:', error);
        alert('Failed to generate report: ' + error.message);
    }
}

function resetAll() {
    // Cancel current job if exists
    if (currentJobId) {
        $.ajax({
            url: `/api/cancel/${currentJobId}`,
            type: 'POST',
            async: false  // Wait for cancellation
        });
    }
    
    clearFile();
    currentJobId = null;
    uploadedFilePath = null;
    currentJsonPath = null;
    currentSessionDir = null;
    if (statusInterval) {
        clearInterval(statusInterval);
    }
    $('#progressCard').hide();
    $('#resultsCard').hide();
    $('#mainCard').show();
}

// Client-side report generation
function generatePDF(reportData, includeAI = true) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Title
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.text('Video Analysis Report', 105, 20, { align: 'center' });
    
    // Subtitle
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(reportData.title || 'Video Analysis', 105, 28, { align: 'center' });
    doc.setTextColor(0, 0, 0);
    
    // Metadata Box
    doc.setFontSize(10);
    let y = 40;
    
    const metadata = reportData.metadata || {};
    const duration = metadata.duration || 0;
    const durationFormatted = formatDuration(duration);
    const modelSize = metadata.model_size || 'base';
    const timestamp = metadata.timestamp || reportData.date || new Date().toISOString();
    const scenesCount = reportData.scenes ? reportData.scenes.length : 0;
    const sectionsCount = reportData.sections ? reportData.sections.length : 0;
    
    // Draw info box
    doc.setDrawColor(220, 220, 220);
    doc.rect(15, y - 5, 180, 28, 'S');
    
    doc.text(`📹 Duration: ${durationFormatted}`, 20, y);
    doc.text(`🎬 Scenes: ${scenesCount}`, 110, y);
    y += 7;
    doc.text(`🤖 Model: ${modelSize}`, 20, y);
    doc.text(`📝 Sections: ${sectionsCount}`, 110, y);
    y += 7;
    doc.text(`📅 Generated: ${new Date(timestamp).toLocaleString()}`, 20, y);
    y += 12;
    
    // Table of Contents
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('📑 Table of Contents', 20, y);
    doc.setFont(undefined, 'normal');
    y += 8;
    doc.setFontSize(10);
    
    let tocItems = [];
    if (includeAI && reportData.ai_summary) tocItems.push('🤖 AI Summary');
    tocItems.push('📊 Summary');
    tocItems.push('🔑 Key Points');
    if (reportData.sections && reportData.sections.length > 0) tocItems.push('📖 Detailed Analysis');
    tocItems.push('📄 Full Transcript');
    
    tocItems.forEach((item, idx) => {
        doc.text(`${idx + 1}. ${item}`, 25, y);
        y += 6;
    });
    y += 10;
    
    // AI Summary (if included)
    if (includeAI && reportData.ai_summary) {
        if (y > 200) {
            doc.addPage();
            y = 20;
        }
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(26, 115, 232);
        doc.text('🤖 AI-Generated Summary', 20, y);
        doc.setTextColor(0, 0, 0);
        doc.setFont(undefined, 'normal');
        y += 10;
        doc.setFontSize(10);
        const aiSummaryText = reportData.ai_summary.summary || reportData.ai_summary;
        const aiSummaryLines = doc.splitTextToSize(aiSummaryText, 170);
        doc.text(aiSummaryLines, 20, y);
        y += aiSummaryLines.length * 5 + 10;
        
        // AI Key Points
        if (reportData.ai_summary.key_points && reportData.ai_summary.key_points.length > 0) {
            doc.setFontSize(12);
            doc.setTextColor(26, 115, 232);
            doc.text('AI Key Points', 20, y);
            doc.setTextColor(0, 0, 0);
            y += 8;
            doc.setFontSize(10);
            reportData.ai_summary.key_points.forEach((point, idx) => {
                if (y > 270) {
                    doc.addPage();
                    y = 20;
                }
                const timestamp = point.timestamp ? ` [${point.timestamp}]` : '';
                const pointText = point.point || point;
                const pointLines = doc.splitTextToSize(`${idx + 1}. ${pointText}${timestamp}`, 165);
                doc.text(pointLines, 20, y);
                y += pointLines.length * 5 + 3;
            });
            y += 10;
        }
    }
    
    // Summary
    if (y > 220) {
        doc.addPage();
        y = 20;
    }
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.text('📊 Summary', 20, y);
    doc.setFont(undefined, 'normal');
    y += 10;
    doc.setFontSize(10);
    const summary = reportData.summary || 'No summary available';
    const summaryLines = doc.splitTextToSize(summary, 170);
    doc.text(summaryLines, 20, y);
    y += summaryLines.length * 5 + 10;
    
    // Key Points
    if (reportData.key_points && reportData.key_points.length > 0) {
        if (y > 220) {
            doc.addPage();
            y = 20;
        }
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text('🔑 Key Points', 20, y);
        doc.setFont(undefined, 'normal');
        y += 10;
        doc.setFontSize(10);
        reportData.key_points.forEach((point, idx) => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }
            const pointLines = doc.splitTextToSize(`${idx + 1}. ${point}`, 165);
            doc.text(pointLines, 20, y);
            y += pointLines.length * 5 + 3;
        });
        y += 10;
    }
    
    // Scene Analysis
    if (reportData.scenes && reportData.scenes.length > 0) {
        if (y > 220) {
            doc.addPage();
            y = 20;
        }
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text('🎬 Scene Analysis', 20, y);
        doc.setFont(undefined, 'normal');
        y += 10;
        doc.setFontSize(9);
        
        const maxScenes = 15; // Show first 15 scenes
        reportData.scenes.slice(0, maxScenes).forEach((scene, idx) => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }
            const sceneTime = formatTime(scene.timestamp || 0);
            doc.text(`Scene ${idx + 1} [${sceneTime}]`, 20, y);
            y += 5;
        });
        
        if (reportData.scenes.length > maxScenes) {
            y += 3;
            doc.setTextColor(100, 100, 100);
            doc.text(`... and ${reportData.scenes.length - maxScenes} more scenes`, 20, y);
            doc.setTextColor(0, 0, 0);
        }
        y += 10;
    }
    
    // Detailed Sections (if available)
    if (reportData.sections && reportData.sections.length > 0 && reportData.sections[0].summary) {
        if (y > 220) {
            doc.addPage();
            y = 20;
        }
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text('📖 Detailed Analysis by Section', 20, y);
        doc.setFont(undefined, 'normal');
        y += 10;
        
        reportData.sections.forEach((section, idx) => {
            if (y > 250) {
                doc.addPage();
                y = 20;
            }
            
            doc.setFontSize(12);
            doc.setFont(undefined, 'bold');
            doc.text(`Section ${idx + 1} [${formatTime(section.start_time)} - ${formatTime(section.end_time)}]`, 20, y);
            y += 7;
            
            if (section.summary) {
                doc.setFontSize(10);
                doc.setFont(undefined, 'bold');
                doc.text('Summary:', 20, y);
                y += 5;
                doc.setFont(undefined, 'normal');
                const summLines = doc.splitTextToSize(section.summary, 165);
                summLines.forEach(line => {
                    if (y > 270) { doc.addPage(); y = 20; }
                    doc.text(line, 25, y);
                    y += 4;
                });
                y += 3;
            }
            
            if (section.key_points && section.key_points.length > 0) {
                doc.setFontSize(10);
                doc.setFont(undefined, 'bold');
                doc.text('Key Points:', 20, y);
                y += 5;
                doc.setFont(undefined, 'normal');
                section.key_points.forEach((point, pidx) => {
                    if (y > 270) { doc.addPage(); y = 20; }
                    const ptLines = doc.splitTextToSize(`• ${point}`, 160);
                    ptLines.forEach(line => {
                        if (y > 270) { doc.addPage(); y = 20; }
                        doc.text(line, 25, y);
                        y += 4;
                    });
                });
                y += 5;
            }
        });
        y += 10;
    }
    
    // Full Transcript
    doc.addPage();
    y = 20;
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.text('📄 Full Transcript', 20, y);
    doc.setFont(undefined, 'normal');
    y += 10;
    doc.setFontSize(9);
    
    // Use full_transcript if available, otherwise use sections
    if (reportData.full_transcript) {
        const transcriptLines = doc.splitTextToSize(reportData.full_transcript, 170);
        transcriptLines.forEach(line => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }
            doc.text(line, 20, y);
            y += 4;
        });
    } else if (reportData.sections && reportData.sections.length > 0) {
        reportData.sections.forEach(section => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }
            const timestamp = `[${formatTime(section.start_time)} - ${formatTime(section.end_time)}]`;
            doc.setFont(undefined, 'bold');
            doc.text(timestamp, 20, y);
            y += 5;
            doc.setFont(undefined, 'normal');
            const textLines = doc.splitTextToSize(section.text, 165);
            textLines.forEach(line => {
                if (y > 270) {
                    doc.addPage();
                    y = 20;
                }
                doc.text(line, 25, y);
                y += 4;
            });
            y += 3;
        });
    }
    
    return doc;
}

function generateDOCX(reportData) {
    // Create a simple XML-based DOCX structure
    const metadata = reportData.metadata || {};
    const duration = metadata.duration || 0;
    const durationFormatted = formatDuration(duration);
    const modelSize = metadata.model_size || 'base';
    const timestamp = metadata.timestamp || reportData.date || new Date().toISOString();
    const title = reportData.title || 'Video Analysis';
    const summary = reportData.summary || 'No summary available';
    
    const content = `
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
        <w:t>Video Analysis Report</w:t>
      </w:r>
    </w:p>
    <w:p><w:r><w:t>Title: ${escapeXml(title)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Duration: ${escapeXml(durationFormatted)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Model: ${escapeXml(modelSize)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Generated: ${escapeXml(new Date(timestamp).toLocaleString())}</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>Summary</w:t></w:r></w:p>
    <w:p><w:r><w:t>${escapeXml(summary)}</w:t></w:r></w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
    ${reportData.key_points && reportData.key_points.length > 0 ? `
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>Key Points</w:t></w:r></w:p>
    ${reportData.key_points.map((point, idx) => 
      `<w:p><w:r><w:t>${idx + 1}. ${escapeXml(point)}</w:t></w:r></w:p>`
    ).join('')}
    <w:p><w:r><w:t></w:t></w:r></w:p>
    ` : ''}
    ${reportData.sections && reportData.sections.length > 0 && reportData.sections[0].summary ? `
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>Detailed Analysis by Section</w:t></w:r></w:p>
    ${reportData.sections.map((section, idx) => `
      <w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Section ${idx + 1} [${formatTime(section.start_time)} - ${formatTime(section.end_time)}]</w:t></w:r></w:p>
      ${section.summary ? `<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Summary:</w:t></w:r></w:p><w:p><w:r><w:t>${escapeXml(section.summary)}</w:t></w:r></w:p>` : ''}
      ${section.key_points && section.key_points.length > 0 ? `<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Key Points:</w:t></w:r></w:p>${section.key_points.map(pt => `<w:p><w:r><w:t>• ${escapeXml(pt)}</w:t></w:r></w:p>`).join('')}` : ''}
      <w:p><w:r><w:t></w:t></w:r></w:p>
    `).join('')}
    <w:p><w:r><w:t></w:t></w:r></w:p>
    ` : ''}
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>Full Transcript</w:t></w:r></w:p>
    ${reportData.full_transcript ? 
      `<w:p><w:r><w:t>${escapeXml(reportData.full_transcript)}</w:t></w:r></w:p>` :
      (reportData.sections || []).map(section => 
        `<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>[${formatTime(section.start_time)} - ${formatTime(section.end_time)}]</w:t></w:r></w:p><w:p><w:r><w:t>${escapeXml(section.text)}</w:t></w:r></w:p>`
      ).join('')
    }
  </w:body>
</w:document>`;
    
    return content;
}

function generateTXT(reportData, includeAI = true) {
    const metadata = reportData.metadata || {};
    const duration = metadata.duration || 0;
    const durationFormatted = formatDuration(duration);
    const modelSize = metadata.model_size || 'base';
    const timestamp = metadata.timestamp || reportData.date || new Date().toISOString();
    const title = reportData.title || 'Video Analysis';
    const summary = reportData.summary || 'No summary available';
    const scenesCount = reportData.scenes ? reportData.scenes.length : 0;
    const sectionsCount = reportData.sections ? reportData.sections.length : 0;
    
    let text = '╔════════════════════════════════════════════════╗\n';
    text += '║       VIDEO ANALYSIS REPORT                    ║\n';
    text += '╚════════════════════════════════════════════════╝\n\n';
    text += `📹 Title: ${title}\n`;
    text += `⏱️  Duration: ${durationFormatted}\n`;
    text += `🤖 Model: ${modelSize}\n`;
    text += `🎬 Scenes: ${scenesCount}\n`;
    text += `📝 Sections: ${sectionsCount}\n`;
    text += `📅 Generated: ${new Date(timestamp).toLocaleString()}\n\n`;
    
    // Table of Contents
    text += '📑 TABLE OF CONTENTS\n';
    text += '═'.repeat(70) + '\n';
    let tocNum = 1;
    if (includeAI && reportData.ai_summary) text += `${tocNum++}. 🤖 AI-Generated Summary\n`;
    text += `${tocNum++}. 📊 Summary\n`;
    text += `${tocNum++}. 🔑 Key Points\n`;
    if (reportData.scenes && reportData.scenes.length > 0) text += `${tocNum++}. 🎬 Scene Analysis\n`;
    if (reportData.sections && reportData.sections.length > 0) text += `${tocNum++}. 📖 Detailed Analysis\n`;
    text += `${tocNum}. 📄 Full Transcript\n\n`;
    
    // AI Summary (if included)
    if (includeAI && reportData.ai_summary) {
        text += '\n' + '═'.repeat(70) + '\n';
        text += '🤖 AI-GENERATED SUMMARY\n';
        text += '═'.repeat(70) + '\n\n';
        const aiSummaryText = reportData.ai_summary.summary || reportData.ai_summary;
        text += `${aiSummaryText}\n\n`;
        
        if (reportData.ai_summary.key_points && reportData.ai_summary.key_points.length > 0) {
            text += 'AI KEY POINTS:\n';
            text += '-'.repeat(70) + '\n';
            reportData.ai_summary.key_points.forEach((point, idx) => {
                const timestamp = point.timestamp ? ` [${point.timestamp}]` : '';
                const pointText = point.point || point;
                text += `${idx + 1}. ${pointText}${timestamp}\n`;
            });
            text += '\n';
        }
    }
    
    text += '\n' + '═'.repeat(70) + '\n';
    text += '📊 SUMMARY\n';
    text += '═'.repeat(70) + '\n';
    text += `${summary}\n\n`;
    
    if (reportData.key_points && reportData.key_points.length > 0) {
        text += '\n' + '═'.repeat(70) + '\n';
        text += '🔑 KEY POINTS\n';
        text += '═'.repeat(70) + '\n';
        reportData.key_points.forEach((point, idx) => {
            text += `${idx + 1}. ${point}\n`;
        });
        text += '\n';
    }
    
    // Scene Analysis
    if (reportData.scenes && reportData.scenes.length > 0) {
        text += '\n' + '═'.repeat(70) + '\n';
        text += '🎬 SCENE ANALYSIS\n';
        text += '═'.repeat(70) + '\n';
        const maxScenes = 20;
        reportData.scenes.slice(0, maxScenes).forEach((scene, idx) => {
            const sceneTime = formatTime(scene.timestamp || 0);
            text += `Scene ${idx + 1} [${sceneTime}]\n`;
        });
        if (reportData.scenes.length > maxScenes) {
            text += `\n... and ${reportData.scenes.length - maxScenes} more scenes\n`;
        }
        text += '\n';
    }
    
    // Detailed sections
    if (reportData.sections && reportData.sections.length > 0 && reportData.sections[0].summary) {
        text += '\n' + '═'.repeat(70) + '\n';
        text += '📖 DETAILED ANALYSIS BY SECTION\n';
        text += '═'.repeat(70) + '\n';
        reportData.sections.forEach((section, idx) => {
            text += `\nSection ${idx + 1} [${formatTime(section.start_time)} - ${formatTime(section.end_time)}]\n`;
            if (section.summary) {
                text += `Summary: ${section.summary}\n`;
            }
            if (section.key_points && section.key_points.length > 0) {
                text += 'Key Points:\n';
                section.key_points.forEach(point => {
                    text += `  • ${point}\n`;
                });
            }
            text += '\n';
        });
        text += '\n';
    }
    
    text += '\n' + '═'.repeat(70) + '\n';
    text += '📄 FULL TRANSCRIPT\n';
    text += '═'.repeat(70) + '\n';
    if (reportData.full_transcript) {
        text += reportData.full_transcript + '\n';
    } else if (reportData.sections && reportData.sections.length > 0) {
        reportData.sections.forEach(section => {
            text += `[${formatTime(section.start_time)} - ${formatTime(section.end_time)}]\n`;
            text += section.text + '\n\n';
        });
    }
    
    return text;
}

function escapeXml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

function formatTime(seconds) {
    if (!seconds) return '00:00:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

async function convertReport() {
    if (!currentJsonPath) {
        showNotification('No report available to convert', 'error');
        return;
    }
    
    const format = $('#convertFormat').val();
    const btn = $('#convertBtn');
    const originalHtml = btn.html();
    
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Generating...');
    
    try {
        // Fetch the JSON report
        const response = await fetch(`/api/download/${encodeURIComponent(currentJsonPath)}`);
        if (!response.ok) throw new Error('Failed to load report');
        
        const reportData = await response.json();
        const baseFilename = currentJsonPath.replace('.json', '');
        
        if (format === 'pdf') {
            const doc = generatePDF(reportData);
            doc.save(`${baseFilename}.pdf`);
            showNotification('PDF generated and downloaded', 'success');
        } else if (format === 'docx') {
            const docContent = generateDOCX(reportData);
            
            // Create minimal DOCX structure
            const zip = new PizZip();
            zip.file('word/document.xml', docContent);
            zip.file('[Content_Types].xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>`);
            zip.file('_rels/.rels', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>`);
            
            const blob = zip.generate({ type: 'blob', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
            saveAs(blob, `${baseFilename}.docx`);
            showNotification('DOCX generated and downloaded', 'success');
        } else if (format === 'txt') {
            const text = generateTXT(reportData);
            const blob = new Blob([text], { type: 'text/plain' });
            saveAs(blob, `${baseFilename}.txt`);
            showNotification('TXT generated and downloaded', 'success');
        }
    } catch (error) {
        console.error('Conversion error:', error);
        showNotification('Failed to generate report: ' + error.message, 'error');
    } finally {
        btn.prop('disabled', false).html(originalHtml);
    }
}

// Bind convert button
$(document).on('click', '#convertBtn', convertReport);

// Helper functions for cloud URLs
function isCloudUrl(url) {
    return url.includes('drive.google.com') || 
           url.includes('docs.google.com') || 
           url.includes('dropbox.com');
}

function getCloudProvider(url) {
    if (url.includes('drive.google.com') || url.includes('docs.google.com')) {
        return 'Google Drive';
    } else if (url.includes('dropbox.com')) {
        return 'Dropbox';
    }
    return 'Cloud Storage';
}

// ============================================
// AI Features - Summary and Chat
// ============================================

function loadAISummary(sessionDir) {
    const summaryPath = sessionDir + '/reports/ai_summary.json';
    
    $.getJSON(`/api/download/${encodeURIComponent(summaryPath)}?attachment=false`, function(data) {
        displayAISummary(data);
    }).fail(function(xhr) {
        $('#reportAi-summary').html(`
            <div style="padding: 20px; text-align: center; color: #5f6368;">
                <i class="fas fa-robot" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                <p><strong>AI Summary not available</strong></p>
                <p style="font-size: 14px;">The Phi-2 model may not be loaded.</p>
                <p style="font-size: 14px;">Run: <code>python download_model.py</code></p>
            </div>
        `);
    });
    
    // Setup chat with report path
    currentJsonPath = sessionDir + '/reports/report.json';
    setupChat();
}

function displayAISummary(data) {
    let html = '<div style="padding: 20px;">';
    
    // Executive Summary
    html += '<div style="margin-bottom: 24px;">';
    html += '<h3 style="color: #1a73e8; margin-bottom: 12px;"><i class="fas fa-robot"></i> AI Executive Summary</h3>';
    html += `<p style="line-height: 1.6; color: #202124;">${data.summary || 'No summary available'}</p>`;
    html += '</div>';
    
    // Key Points
    if (data.key_points && data.key_points.length > 0) {
        html += '<div>';
        html += '<h4 style="color: #1a73e8; margin-bottom: 12px;"><i class="fas fa-list-ul"></i> Key Points</h4>';
        html += '<ul style="line-height: 1.8;">';
        data.key_points.forEach(point => {
            html += `<li style="margin-bottom: 8px;">${point}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    html += '</div>';
    $('#reportAi-summary').html(html);
}

function setupChat() {
    // Clear previous messages
    $('.chat-messages').empty();
    
    // Welcome message
    const welcomeMsg = $('<div class="chat-message ai-message"></div>').html(`
        <div style="display: flex; align-items: start; gap: 12px;">
            <i class="fas fa-robot" style="color: #1a73e8; font-size: 24px;"></i>
            <div>
                <p><strong>AI Assistant</strong></p>
                <p>Ask me anything about the video! Examples:</p>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li>What is this video about?</li>
                    <li>Summarize the main points</li>
                    <li>What happened at 2:30?</li>
                    <li>Who spoke the most?</li>
                </ul>
            </div>
        </div>
    `);
    $('.chat-messages').append(welcomeMsg);
    
    // Bind send button
    $('#chatSendBtn').off('click').on('click', sendChatMessage);
    $('#chatInput').off('keypress').on('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

function sendChatMessage() {
    const input = $('#chatInput');
    const question = input.val().trim();
    
    if (!question) return;
    
    // Display user message
    const userMsg = $('<div class="chat-message user-message"></div>').html(`
        <div style="display: flex; align-items: start; gap: 12px; justify-content: flex-end;">
            <div style="background: #e8f0fe; padding: 12px 16px; border-radius: 18px; max-width: 70%;">
                <p style="margin: 0;">${question}</p>
            </div>
            <i class="fas fa-user-circle" style="color: #5f6368; font-size: 24px;"></i>
        </div>
    `);
    $('.chat-messages').append(userMsg);
    
    // Clear input
    input.val('');
    
    // Show loading
    const loadingMsg = $('<div class="chat-message ai-message" id="loadingMsg"></div>').html(`
        <div style="display: flex; align-items: start; gap: 12px;">
            <i class="fas fa-robot" style="color: #1a73e8; font-size: 24px;"></i>
            <div>
                <i class="fas fa-spinner fa-spin"></i> Thinking...
            </div>
        </div>
    `);
    $('.chat-messages').append(loadingMsg);
    
    // Scroll to bottom
    const chatContainer = $('.chat-messages')[0];
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Send to API
    $.ajax({
        url: '/api/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            question: question,
            report_path: currentJsonPath
        }),
        success: function(response) {
            $('#loadingMsg').remove();
            
            const aiMsg = $('<div class="chat-message ai-message"></div>').html(`
                <div style="display: flex; align-items: start; gap: 12px;">
                    <i class="fas fa-robot" style="color: #1a73e8; font-size: 24px;"></i>
                    <div style="background: #f1f3f4; padding: 12px 16px; border-radius: 18px; max-width: 70%;">
                        <p style="margin: 0; line-height: 1.6;">${response.answer}</p>
                    </div>
                </div>
            `);
            $('.chat-messages').append(aiMsg);
            
            // Scroll to bottom
            const chatContainer = $('.chat-messages')[0];
            chatContainer.scrollTop = chatContainer.scrollHeight;
        },
        error: function(xhr) {
            $('#loadingMsg').remove();
            
            const errorMsg = xhr.responseJSON?.error || 'Failed to get response';
            const aiMsg = $('<div class="chat-message ai-message"></div>').html(`
                <div style="display: flex; align-items: start; gap: 12px;">
                    <i class="fas fa-robot" style="color: #ea4335; font-size: 24px;"></i>
                    <div style="background: #fce8e6; padding: 12px 16px; border-radius: 18px; max-width: 70%;">
                        <p style="margin: 0; color: #d93025;"><strong>Error:</strong> ${errorMsg}</p>
                    </div>
                </div>
            `);
            $('.chat-messages').append(aiMsg);
            
            // Scroll to bottom
            const chatContainer = $('.chat-messages')[0];
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });
}
