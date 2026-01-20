// Simple frontend handlers (placeholder)
document.addEventListener('DOMContentLoaded', () => {
    const announcementsBtn = document.getElementById('announcementsBtn');
    const campusInfoBtn = document.getElementById('campusInfoBtn');
    const usersBtn = document.getElementById('usersBtn');
    const documentsAdminBtn = document.getElementById('documentsAdminBtn');
    const attendanceStatsBtn = document.getElementById('attendanceStatsBtn');
    const configBtn = document.getElementById('configBtn');
    const publishAnnouncementBtn = document.getElementById('publishAnnouncementBtn');

    const notify = (msg) => alert(msg);

    if (announcementsBtn) announcementsBtn.onclick = () => window.location.href = 'admin-annonces.html';
    if (campusInfoBtn) campusInfoBtn.onclick = () => window.location.href = 'admin-infos.html';
    if (usersBtn) usersBtn.onclick = () => window.location.href = 'admin-users.html';
    if (documentsAdminBtn) documentsAdminBtn.onclick = () => window.location.href = 'admin-demandes.html';
    if (attendanceStatsBtn) attendanceStatsBtn.onclick = () => window.location.href = 'admin-presence.html';
    if (configBtn) configBtn.onclick = () => window.location.href = 'admin-config.html';
    if (publishAnnouncementBtn) publishAnnouncementBtn.onclick = () => notify('Annonce publiée (placeholder). Ajoutez la logique plus tard.');
});

