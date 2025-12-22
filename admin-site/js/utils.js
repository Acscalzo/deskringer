// Utility functions for the admin dashboard

/**
 * Format a UTC datetime string to local timezone
 * @param {string} dateString - ISO datetime string from backend
 * @param {boolean} includeTime - Whether to include time (default: true)
 * @returns {string} Formatted date/time string
 */
function formatDateTime(dateString, includeTime = true) {
    if (!dateString) return 'N/A';

    // Parse as UTC by adding 'Z' if not present
    let isoString = dateString;
    if (!isoString.endsWith('Z') && !isoString.includes('+')) {
        isoString += 'Z';
    }

    const date = new Date(isoString);

    if (isNaN(date.getTime())) {
        return 'Invalid date';
    }

    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: includeTime ? 'numeric' : undefined,
        minute: includeTime ? '2-digit' : undefined,
        hour12: true
    };

    return date.toLocaleString('en-US', options);
}

/**
 * Format a date without time
 * @param {string} dateString - ISO datetime string from backend
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    return formatDateTime(dateString, false);
}

/**
 * Format duration in seconds to human readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration (e.g., "2m 30s")
 */
function formatDuration(seconds) {
    if (!seconds || seconds === 0) return '0s';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes === 0) {
        return `${remainingSeconds}s`;
    }

    return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Get relative time (e.g., "2 hours ago")
 * @param {string} dateString - ISO datetime string from backend
 * @returns {string} Relative time string
 */
function getRelativeTime(dateString) {
    if (!dateString) return 'N/A';

    let isoString = dateString;
    if (!isoString.endsWith('Z') && !isoString.includes('+')) {
        isoString += 'Z';
    }

    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays}d ago`;

    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths}mo ago`;
}
