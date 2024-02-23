// SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

use lru::LruCache;
use std::{net::IpAddr, num::NonZeroUsize, time::Duration, sync::{Arc, Mutex}};

use std::time::Instant;

struct Inner {
    requests: LruCache<IpAddr, u16>,
    rate_limit: u16,
    last_cleared: Instant,
}

pub struct IpRateLimit {
    inner: Arc<Mutex<Inner>>
}

impl IpRateLimit {
    pub fn new(size: NonZeroUsize, rate_limit: u16) -> IpRateLimit {
        IpRateLimit {
            inner: Arc::new(Mutex::new(Inner {
                requests: LruCache::new(size),
                rate_limit,
                last_cleared: Instant::now(),
            }))
        }
    }

    pub fn should_limit(&self, ip: &IpAddr) -> bool {
        let mut inner = self.inner.lock().unwrap();

        // Check if data is older than a minute, then delete it
        if inner.last_cleared.elapsed() >= Duration::from_secs(60) {
            inner.requests.clear();
            inner.last_cleared = Instant::now();
        }

        // Incerement existing request counter for address or create a new one
        if let Some(count) = inner.requests.get_mut(ip) {
            *count += 1;
        } else {
            inner.requests.put(*ip, 1);
        }


        // Check if ip has reached rate limit
        let rate_limit = inner.rate_limit;
        inner.requests
            .get(&ip)
            .map(|count| *count >= rate_limit)
            .unwrap_or(false)
    }
}
