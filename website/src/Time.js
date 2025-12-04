// SPDX-FileCopyrightText: 2025 Transitous contributors
// SPDX-License-Identifier: AGPL-3.0-or-later

// PureScript FFI for timezone-aware time formatting
// Uses Intl.DateTimeFormat with timeZone and timeZoneName.

/**
 * @param {string} utcString - UTC datetime string (ISO-8601 or Date-parsable)
 * @param {?string} maybeStopTz - Optional IANA timezone name for the stop
 * @returns {function(): { stopTime: string, userTime: string, showBoth: boolean }}
 */
export const formatTimes = (utcString) => (maybeStopTz) => () => {
  // Parse input as UTC. new Date(utcString) interprets ISO-8601 with Z correctly as UTC.
  // If utcString is epoch milliseconds as string/number, Date will handle that as well.
  const date = new Date(utcString);

  // Browser/user timezone
  const userTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const stopTz = maybeStopTz ?? userTz;

  const baseOptions = {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  };

  const stopFmt = new Intl.DateTimeFormat([], { ...baseOptions, timeZone: stopTz });
  const userFmt = new Intl.DateTimeFormat([], { ...baseOptions, timeZone: userTz });

  const stopTime = stopFmt.format(date);
  const userTime = userFmt.format(date);
  const showBoth = stopTz !== userTz;

  return { stopTime, userTime, showBoth };
};
