$(function(){
    var ul = $('#upload ul');
    var selectedFile = null;
    var selectedTags = new Set();  // 确保在最开始就初始化 selectedTags
    
    // 清空已选标签区域
    $('#selectedTags').empty();
    
    // 重置标签计数
    updateTagsCount();
    
    // 获取并显示推荐标签
    function updateSuggestedTags() {
        const title = $('input[name="title"]').val();
        const description = $('input[name="describe"]').val();
        const formData = new FormData();
        
        console.log('准备发送的标题:', title);  // 添加调试信息
        console.log('准备发送的描述:', description);  // 添加调试信息
        
        formData.append('title', title);
        formData.append('description', description);  // 确保使用 'description' 作为字段名
        
        if (selectedFile && selectedFile.files[0]) {
            formData.append('upl', selectedFile.files[0]);
        }
        
        $.ajax({
            url: '/get_suggested_tags',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('收到服务器响应:', response);  // 添加调试信息
                
                const container = $('#suggestedTagsContainer');
                container.empty();
                
                // 显示图片识别标签
                if (response.image_tags && response.image_tags.length > 0) {
                    console.log('处理图片标签数量:', response.image_tags.length);
                    
                    container.append(`
                        <div class="tags-section">
                            <h5><i class="fas fa-image"></i> 图片识别结果（点击添加标签）</h5>
                            <div class="tags-container"></div>
                        </div>
                    `);
                    
                    const imageTagsContainer = container.find('.tags-section .tags-container').last();
                    
                    response.image_tags.forEach((tag, index) => {
                        console.log(`处理第 ${index + 1} 个标签:`, tag);
                        
                        if (!selectedTags.has(tag.name)) {
                            const tagElement = $(`
                                <span class="tag-suggestion top-tag" 
                                      data-rank="${index + 1}" 
                                      title="点击添加此标签">
                                    <i class="fas fa-tag"></i>
                                    ${tag.name}
                                    <small class="confidence">可信度: ${tag.confidence}</small>
                                </span>
                            `);
                            
                            // 根据排名添加不同的样式
                            if (index === 0) {
                                tagElement.css('border-color', '#ffd700'); // 金色
                            } else if (index === 1) {
                                tagElement.css('border-color', '#c0c0c0'); // 银色
                            } else if (index === 2) {
                                tagElement.css('border-color', '#cd7f32'); // 铜色
                            }
                            
                            tagElement.click(() => {
                                if (!selectedTags.has(tag.name)) {
                                    addTag(tag.name);
                                    tagElement.addClass('selected').fadeOut(300, function() {
                                        $(this).remove();
                                    });
                                }
                            });
                            
                            imageTagsContainer.append(tagElement);
                        }
                    });
                }
                
                // 显示文本关键词标签
                if (response.text_tags && response.text_tags.length > 0) {
                    console.log('处理文本标签:', response.text_tags);  // 添加调试日志
                    
                    container.append(`
                        <div class="tags-section">
                            <h5><i class="fas fa-font"></i> 文本关键词</h5>
                            <div class="tags-container"></div>
                        </div>
                    `);
                    
                    const textTagsContainer = container.find('.tags-section .tags-container').last();
                    
                    response.text_tags.forEach(tag => {
                        if (!selectedTags.has(tag)) {  // 只显示未选择的标签
                            const tagElement = $(`
                                <span class="tag-suggestion">
                                    <i class="fas fa-tag"></i>
                                    ${tag}
                                </span>
                            `);
                            
                            tagElement.click(() => {
                                if (!selectedTags.has(tag)) {
                                    addTag(tag);
                                    tagElement.fadeOut(300, function() {
                                        $(this).remove();
                                    });
                                }
                            });
                            
                            textTagsContainer.append(tagElement);
                        }
                    });
                }
                
                if ((!response.image_tags || response.image_tags.length === 0) && 
                    (!response.text_tags || response.text_tags.length === 0)) {
                    container.append(`
                        <p class="no-tags">
                            <i class="fas fa-info-circle"></i>
                            上传图片并输入标题描述后将显示推荐标签
                        </p>
                    `);
                }
            },
            error: function(xhr, status, error) {
                console.error('标签请求失败:', error);  // 添加错误日志
                $('#suggestedTagsContainer').empty().append(`
                    <p class="no-tags error">
                        <i class="fas fa-exclamation-circle"></i>
                        获取标签建议失败，请重试
                    </p>
                `);
            }
        });
    }

    // 添加新标签
    function addTag(tagName) {
        if (selectedTags.has(tagName)) {
            Swal.fire({
                icon: 'warning',
                title: '标签已存在',
                text: '请勿重复添加相同标签',
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }
        
        if (selectedTags.size >= 10) {
            Swal.fire({
                icon: 'warning',
                title: '标签数量已达上限',
                text: '最多只能添加10个标签',
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }

        // 只在这里添加标签到已选集合
        selectedTags.add(tagName);
        $('#tagsInput').val(Array.from(selectedTags).join(','));
        
        // 创建新标签元
        const tagElement = $(`
            <span class="selected-tag">
                ${tagName}
                <i class="fas fa-times delete-icon"></i>
            </span>
        `);

        // 添加到已选标签区域
        tagElement.appendTo('#selectedTags');
        
        // 添加出现动画
        tagElement.css({
            opacity: 0,
            transform: 'scale(0.8)'
        }).animate({
            opacity: 1
        }, {
            duration: 200,
            queue: false
        }).css('transform', 'scale(1)');

        // 绑定删除事件
        tagElement.find('.delete-icon').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            selectedTags.delete(tagName);
            tagElement.fadeOut(200, function() {
                $(this).remove();
                $('#tagsInput').val(Array.from(selectedTags).join(','));
                updateTagsCount();
                updateSuggestedTags();  // 更新推荐标签显示
            });
            checkFormValidity();
        });

        updateTagsCount();
        checkFormValidity();
    }

    // 更新标签计数
    function updateTagsCount() {
        $('#tagsCount').text(selectedTags.size);
    }

    // 处理标签输入框
    $('#tagInput').on('keypress', function(e) {
        if (e.which === 13) { // Enter键
            e.preventDefault();
            const tagName = $(this).val().trim();
            if (tagName) {
                addTag(tagName);
                $(this).val(''); // 清空输入框
            }
        }
    });

    // 监听标题和描述的输入变化
    $('input[name="title"], input[name="describe"]').on('input', function() {
        checkFormValidity();
    });

    // 表单验证
    function checkFormValidity() {
        const title = $('input[name="title"]').val();
        const description = $('input[name="describe"]').val();
        const isTitleValid = title && title !== '请输入你的图像标题';
        const isDescriptionValid = description && description !== '请输入你的图像描述';
        
        // 添加调试日志
        console.log('Title:', title, 'isValid:', isTitleValid);
        console.log('Description:', description, 'isValid:', isDescriptionValid);
        console.log('Selected File:', selectedFile);
        
        // 更新提交按钮状态
        $('#submitButton').prop('disabled', !(isTitleValid && isDescriptionValid && selectedFile));
    }

    // 初始化显示
    updateSuggestedTags();
    
    // 修改点击上传按钮的处理
    $('#drop a').click(function(){
        $(this).parent().find('input').click();
    });

    // 修改文件上传处理
    $('#upload').fileupload({
        dropZone: $('#drop'),
        autoUpload: false,
        add: function (e, data) {
            var tpl = $('<li class="working"><input type="text" value="0" data-width="48" data-height="48"' +
                ' data-fgColor="#0788a5" data-readOnly="1" data-bgColor="#3e4043" /><p></p><span></span></li>');

            tpl.find('p').text(data.files[0].name)
                         .append('<i>' + formatFileSize(data.files[0].size) + '</i>');

            data.context = tpl.appendTo(ul);
            tpl.find('input').knob();

            // 保存文件数据
            selectedFile = data;
            
            // 立即检查表单有效性
            checkFormValidity();
            
            // 清空已选标签
            selectedTags.clear();
            $('#selectedTags').empty();
            $('#tagsInput').val('');
            updateTagsCount();
            
            // 清除之前的标签建议
            $('#suggestedTagsContainer').empty();

            // 只在这里触发一次标签更新
            updateSuggestedTags();
            
            tpl.find('span').click(function(){
                tpl.fadeOut(function(){
                    tpl.remove();
                    selectedFile = null;
                    checkFormValidity();
                    // 清空推荐标签
                    $('#suggestedTagsContainer').empty();
                });
            });
        }
    });

    // 修改提交按钮点击处理
    $('#submitButton').click(function() {
        if (selectedFile) {
            // 创建新的 FormData 对象
            const formData = new FormData();
            
            // 添加文件
            formData.append('upl', selectedFile.files[0]);
            
            // 添加标题和描述
            formData.append('title', $('input[name="title"]').val());
            formData.append('describe', $('input[name="describe"]').val());
            
            // 添加标签
            formData.append('tags', Array.from(selectedTags).join(','));
            
            // 发送 AJAX 请求
            $.ajax({
                url: '/upload',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(result) {
                    if (result.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: '图片上传成功！',
                            showConfirmButton: false,
                            timer: 2000
                        }).then(() => {
                            // SweetAlert2 关闭后跳转
                            window.location.href = '/';
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: '图片上传失败',
                            text: result.message,
                            confirmButtonText: '确定'
                        });
                    }
                },
                error: function() {
                    Swal.fire({
                        icon: 'error',
                        title: '上传失败',
                        text: '服务器错误，请稍后重试',
                        confirmButtonText: '确定'
                    });
                }
            });
        }
    });

    $(document).on('drop dragover', function (e) {
        e.preventDefault();
    });

    $(document).ready(function() {
    // 处理登录失败的错误信息
    {% if login_failed %}
        $('#error-message').removeClass('hidden');
    {% endif %}
});

    function formatFileSize(bytes) {
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
    }

    function showSuccessMessage(message) {
        // 创建一个提示消息元素并添加到页面
        var successMessage = $('<div class="success-message">' + message + '</div>').appendTo('body');

        // 在3秒后淡出并移除元素
        setTimeout(function() {
            successMessage.fadeOut(function() {
                successMessage.remove();
            });
        }, 3000);
    }

    function showErrorMessage(message) {
        var errorMessage = $('<div class="error-message">' + message + '</div>').appendTo('body');
        setTimeout(function() {
            errorMessage.fadeOut(function() {
                errorMessage.remove();
            });
        }, 3000);
    }

    // 添加相关的CSS样式
    const style = `
    <style>
    .tags-section {
        margin-bottom: 20px;
        background: #fff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .tags-section h5 {
        color: #0788a5;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .tags-section h5 i {
        font-size: 16px;
    }

    .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .tag-suggestion {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: #f8f9fa;
        border: 1px solid #0788a5;
        color: #0788a5;
        border-radius: 16px;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .tag-suggestion:hover {
        background: #0788a5;
        color: #fff;
        transform: translateY(-1px);
    }

    .tag-suggestion.selected {
        background: #0788a5;
        color: #fff;
    }

    .no-tags {
        text-align: center;
        color: #666;
        padding: 20px;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .no-tags i {
        color: #0788a5;
    }
    </style>
    `;

    // 将样式添加到页面
    $('head').append(style);
});