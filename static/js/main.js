// 页面加载完成后执行
$(document).ready(function () {
    // 添加动画效果
    $('.card').addClass('animate__animated animate__fadeIn');

    // 消息提示框
    function showMessage(message, type = 'success') {
        const alertDiv = $('<div>')
            .addClass(`alert alert-${type} alert-dismissible fade show`)
            .attr('role', 'alert')
            .html(`
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `);

        // 添加到页面顶部
        $('main').prepend(alertDiv);

        // 5秒后自动消失
        setTimeout(function () {
            alertDiv.alert('close');
        }, 3000);
    }

    // 导出全局函数
    window.showMessage = showMessage;

    // 处理AJAX错误
    $(document).ajaxError(function (event, jqXHR, settings, thrownError) {
        showMessage('请求失败，请重试。错误: ' + thrownError, 'danger');
    });

    // 为所有外部链接添加新窗口打开
    $('a[href^="http"]').attr('target', '_blank');

    // 返回顶部按钮
    const backToTopBtn = $('<button>')
        .addClass('btn btn-primary back-to-top-btn')
        .html('<i class="fas fa-arrow-up"></i>')
        .css({
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'display': 'none',
            'border-radius': '50%',
            'width': '40px',
            'height': '40px',
            'padding': '0',
            'z-index': '1000'
        })
        .on('click', function () {
            $('html, body').animate({ scrollTop: 0 }, 'slow');
        });

    $('body').append(backToTopBtn);

    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            backToTopBtn.fadeIn();
        } else {
            backToTopBtn.fadeOut();
        }
    });
}); 