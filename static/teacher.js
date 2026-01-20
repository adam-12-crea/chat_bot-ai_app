// Simple frontend handlers (placeholder)
document.addEventListener('DOMContentLoaded', () => {
    const uploadCourseBtn = document.getElementById('uploadCourseBtn');
    const manageMaterialsBtn = document.getElementById('manageMaterialsBtn');
    const attendanceBtn = document.getElementById('attendanceBtn');
    const reportsBtn = document.getElementById('reportsBtn');
    const saveCourseBtn = document.getElementById('saveCourseBtn');
    const courseFile = document.getElementById('courseFile');

    const notify = (msg) => alert(msg);

    if (uploadCourseBtn) uploadCourseBtn.onclick = () => window.location.href = 'teacher-upload.html';
    if (manageMaterialsBtn) manageMaterialsBtn.onclick = () => window.location.href = 'teacher-ressources.html';
    if (attendanceBtn) attendanceBtn.onclick = () => window.location.href = 'teacher-presence.html';
    if (reportsBtn) reportsBtn.onclick = () => window.location.href = 'teacher-rapports.html';
    if (saveCourseBtn) saveCourseBtn.onclick = () => notify('Cours enregistré (placeholder). Ajoutez la logique plus tard.');

    if (courseFile) {
        courseFile.onchange = () => {
            if (courseFile.files.length) {
                notify(`Fichier sélectionné: ${courseFile.files[0].name}`);
            }
        };
    }
});

