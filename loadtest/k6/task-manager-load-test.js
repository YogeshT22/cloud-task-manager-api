import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
scenarios: {
    health_check: {
      executor: 'constant-vus',
      vus: 50,
      duration: '3m',
      exec: 'healthCheck',
    },
    authenticated_tasks: {
      executor: 'ramping-vus',
      startTime: '10s',
      exec: 'authenticatedTaskFlow',
      stages: [
        { duration: '30s', target: 100 },
        { duration: '1m',  target: 300 },
        { duration: '1m',  target: 500 },
        { duration: '30s', target: 700 },
        { duration: '30s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],      // allow up to 5% errors
    http_req_duration: ['p(95)<2000'],   // loose threshold so it doesn't abort early
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ACCESS_TOKEN = __ENV.ACCESS_TOKEN;
const TASK_ID = __ENV.TASK_ID;

export function healthCheck() {
  const res = http.get(`${BASE_URL}/health`);

  check(res, {
    'health endpoint returned 200': (r) => r.status === 200,
    'health payload is ok': (r) => r.json('status') === 'ok',
  });

  sleep(1);
}

export function authenticatedTaskFlow() {
  if (!ACCESS_TOKEN || !TASK_ID) {
    throw new Error('Set ACCESS_TOKEN and TASK_ID env vars before running the authenticated scenario.');
  }

  const headers = {
    Authorization: `Bearer ${ACCESS_TOKEN}`,
    'Content-Type': 'application/json',
  };

  const listRes = http.get(`${BASE_URL}/tasks/`, { headers });
  check(listRes, {
    'tasks list returned 200': (r) => r.status === 200,
  });

  const taskRes = http.get(`${BASE_URL}/tasks/${TASK_ID}`, { headers });
  check(taskRes, {
    'single task returned 200': (r) => r.status === 200,
  });

  sleep(1);
}
