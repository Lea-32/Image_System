$(function(){
    var ul = $('.upload-list');
    var selectedFile = null;
    var selectedTags = new Set();
    
    // 初始化
    function init() {
        $('#selectedTags').empty();
        updateTagsCount();
        checkFormValidity();
        
        // 点击上传区域触发文件选择
        $('#drop').on('click', function(e) {
            if (e.target === this || $(e.target).closest('.upload-content').length > 0) {
                $('#drop input[type="file"]').click();
            }
        });
        
        // 监听标签输入
        $('#tagInput').on('keypress', function(e) {
            if (e.which === 13) { // 回车键
                e.preventDefault();
                const tagName = $(this).val().trim();
                if (tagName) {
                    addTag(tagName);
                    $(this).val('');
                }
            }
        });
    }
    
    // 预览图片
    function previewImage(file) {
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const previewImage = $('#preview-image');
                const previewContainer = $('#preview-container');
                
                // 显示图片
                previewImage.attr('src', e.target.result);
                previewImage.show();
                previewContainer.hide();
                
                // 更新文件信息
                $('#preview-filename').text(file.name);
                $('#preview-filesize').text(formatFileSize(file.size));
                
                // 获取图片尺寸
                const img = new Image();
                img.onload = function() {
                    $('#preview-dimensions').text(`${this.width} x ${this.height}`);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }
    
    // 监听标题和描述的输入
    $('input[name="title"], input[name="describe"]').on('input', function() {
        checkFormValidity();
    });
    
    // 更新推荐标签
    function updateSuggestedTags() {
        const title = $('input[name="title"]').val();
        const description = $('input[name="describe"]').val();
        const formData = new FormData();
        
        formData.append('title', title);
        formData.append('description', description);
        
        if (selectedFile && selectedFile.files && selectedFile.files[0]) {
            console.log("添加文件到FormData:", selectedFile.files[0].name);
            formData.append('upl', selectedFile.files[0]);
        } else {
            console.log("没有选择文件");
        }
        
        // 显示加载提示
        $('#imageTags').html('<div class="loading-tags">正在分析图片...</div>');
        $('#textTags').html('<div class="loading-tags">正在分析文本...</div>');
        
        $.ajax({
            url: '/get_suggested_tags',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log("收到响应:", response);
                
                // 添加图像标签
                if (response.image_tags && response.image_tags.length > 0) {
                    console.log("添加图像标签:", response.image_tags);
                    const imageTagsContainer = $('#imageTags');
                    imageTagsContainer.empty();
                    response.image_tags.forEach(function(tag) {
                        const confidence = parseFloat(tag.confidence);
                        const tagElement = $('<div class="tag-suggestion">')
                            .text(tag.name)
                            .append($('<span class="confidence">').text(confidence.toFixed(1) + '%'))
                            .click(function() {
                                addTag(tag.name);
                            });
                        imageTagsContainer.append(tagElement);
                    });
                } else {
                    $('#imageTags').html('<div class="no-tags">暂无图像标签</div>');
                }
                
                // 添加文本标签
                if (response.text_tags && response.text_tags.length > 0) {
                    console.log("添加文本标签:", response.text_tags);
                    const textTagsContainer = $('#textTags');
                    textTagsContainer.empty();
                    response.text_tags.forEach(function(tag) {
                        const tagElement = $('<div class="tag-suggestion">')
                            .text(tag)
                            .click(function() {
                                addTag(tag);
                            });
                        textTagsContainer.append(tagElement);
                    });
                } else {
                    $('#textTags').html('<div class="no-tags">暂无文本标签</div>');
                }
            },
            error: function(xhr, status, error) {
                console.error('获取推荐标签失败:', error);
                $('#imageTags').html('<div class="error-tags">获取图像标签失败</div>');
                $('#textTags').html('<div class="error-tags">获取文本标签失败</div>');
            }
        });
    }
    
    // 添加标签
    function addTag(tagName) {
        if (selectedTags.size >= 10) {
            Swal.fire({
                icon: 'warning',
                title: '最多只能添加10个标签',
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }
        
        if (selectedTags.has(tagName)) {
            return;
        }
        
        selectedTags.add(tagName);
        
        const tagElement = $('<div class="tag-item">')
            .text(tagName)
            .append(
                $('<span class="delete-tag">')
                    .html('<i class="fas fa-times"></i>')
                    .click(function() {
                        selectedTags.delete(tagName);
                        tagElement.remove();
                        updateTagsCount();
                        $('#tagsInput').val(Array.from(selectedTags).join(','));
                        checkFormValidity();
                    })
            );
        
        $('#selectedTags').append(tagElement);
        $('#tagsInput').val(Array.from(selectedTags).join(','));
        updateTagsCount();
        checkFormValidity();
    }
    
    // 更新标签计数
    function updateTagsCount() {
        $('#tagsCount').text(selectedTags.size);
    }
    
    // 处理文件上传区域
    var dropArea = $('#drop');
    
    // 处理拖拽事件
    dropArea.on('dragenter dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
    });
    
    dropArea.on('dragleave drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
    });
    
    // 处理文件拖放
    dropArea.on('drop', function(e) {
        const files = e.originalEvent.dataTransfer.files;
        if (files.length) {
            handleFiles(files);
        }
    });
    
    // 处理文件选择
    $('#drop input[type="file"]').on('change', function(e) {
        const files = e.target.files;
        if (files.length) {
            handleFiles(files);
        }
    });
    
    // 处理文件
    function handleFiles(files) {
        const file = files[0];
        
        // 检查文件类型
        if (!file.type.match('image.*')) {
            Swal.fire({
                icon: 'error',
                title: '文件类型错误',
                text: '请选择图片文件',
                confirmButtonText: '确定'
            });
            return;
        }
        
        // 清空现有的文件列表
        ul.empty();
        
        // 创建新的文件项
        var tpl = $('<li class="working"><input type="text" value="0" data-width="48" data-height="48"' +
            ' data-fgColor="#0788a5" data-readOnly="1" data-bgColor="#3e4043" /><p></p><span><i class="fas fa-times"></i></span></li>');
        
        tpl.find('p').text(file.name)
            .append('<i>' + formatFileSize(file.size) + '</i>');
        
        tpl.appendTo(ul);
        tpl.find('input').knob();
        
        selectedFile = {files: [file]};
        checkFormValidity();
        
        // 预览图片
        previewImage(file);
        
        // 更新上传区域样式
        $('#drop').addClass('success');
        
        // 更新推荐标签
        updateSuggestedTags();
        
        // 添加删除按钮功能
        tpl.find('span').click(function(){
            tpl.fadeOut(function(){
                tpl.remove();
                selectedFile = null;
                $('#preview-image').hide();
                $('#preview-container').show();
                $('#preview-filename').text('-');
                $('#preview-filesize').text('-');
                $('#preview-dimensions').text('-');
                $('#drop').removeClass('success');
                checkFormValidity();
                // 清空推荐标签
                $('#imageTags').html('<div class="loading-tags">上传图片后将显示推荐标签</div>');
                $('#textTags').html('<div class="loading-tags">上传图片后将显示推荐标签</div>');
            });
        });
    }
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes >= 1000000000) {
            return (bytes / 1000000000).toFixed(2) + ' GB';
        }
        if (bytes >= 1000000) {
            return (bytes / 1000000).toFixed(2) + ' MB';
        }
        return (bytes / 1000).toFixed(2) + ' KB';
    }
    
    // 表单验证
    function checkFormValidity() {
        const title = $('input[name="title"]').val();
        const description = $('input[name="describe"]').val();
        const isTitleValid = title && title.trim() !== '';
        const isDescriptionValid = description && description.trim() !== '';
        const hasFile = selectedFile !== null;
        
        $('#submitButton').prop('disabled', !(isTitleValid && isDescriptionValid && hasFile));
    }
    
    // 处理表单提交
    $('#submitButton').click(function() {
        if (!selectedFile) {
            return;
        }
        
        const formData = new FormData();
        formData.append('upl', selectedFile.files[0]);
        formData.append('title', $('input[name="title"]').val());
        formData.append('describe', $('input[name="describe"]').val());
        formData.append('tags', Array.from(selectedTags).join(','));
        
        // 禁用提交按钮
        $('#submitButton').prop('disabled', true).text('上传中...');
        
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = Math.round((evt.loaded / evt.total) * 100);
                        $('.working input').val(percentComplete).change();
                        
                        if(percentComplete === 100) {
                            $('.working').removeClass('working');
                        }
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: '上传成功！',
                        text: '图片已成功上传',
                        showConfirmButton: false,
                        timer: 2000
                    }).then(() => {
                        window.location.href = '/';
                    });
                } else {
                    showErrorMessage(response.message || '上传失败，请重试');
                    $('#submitButton').prop('disabled', false).text('提交');
                }
            },
            error: function() {
                showErrorMessage('上传失败，请重试');
                $('#submitButton').prop('disabled', false).text('提交');
            }
        });
    });
    
    // 错误提示
    function showErrorMessage(message) {
        Swal.fire({
            icon: 'error',
            title: '错误',
            text: message,
            confirmButtonText: '确定'
        });
    }
    
    // 初始化
    init();
});