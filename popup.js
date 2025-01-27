document.addEventListener('DOMContentLoaded', () => {
    const videoTitleElement = document.getElementById('videoTitle');
    const downloadButton = document.getElementById('downloadButton');

    function getVideoTitleFromTabTitle(tabTitle) {
        return tabTitle.replace(' - YouTube', '');
    }

    downloadButton.addEventListener('click', () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            const videoUrl = currentTab.url;

            if (videoUrl.includes('youtube.com/watch?v=')) {
                const downloadUrl = `http://localhost:5000/download?url=${encodeURIComponent(videoUrl)}`;
                chrome.downloads.download({ url: downloadUrl });
            } else {
                alert('Esta não é uma URL válida do YouTube.');
            }
        });
    });

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        if (currentTab.url.includes('youtube.com/watch?v=')) {
            const tabTitle = currentTab.title;
            const videoTitle = getVideoTitleFromTabTitle(tabTitle);
            videoTitleElement.textContent = videoTitle || 'Título não disponível';
        } else {
            videoTitleElement.textContent = 'Navegue até um vídeo do YouTube';
        }
    });
});
