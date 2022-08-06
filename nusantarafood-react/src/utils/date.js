export function formatDate(d) {
    const day = d.getDate().toString().padStart(2, '0');
    const month = d.getMonth().toString().padStart(2, '0');
    const year = d.getFullYear();
    let hour = d.getHours();
    let minutes = d.getMinutes();
    let am = 'am'
    if(hour>12) {
        hour -= 12;
        am = 'pm'
    }

    hour = hour.toString().padStart(2, '0');
    minutes = minutes.toString().padStart(2, '0');

    return `${day}/${month}/${year} ${hour}:${minutes}${am}`;
}