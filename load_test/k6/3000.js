import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 3000,        // 시작부터 3000명 동시 접속
  duration: '30s',  // 30초 동안 유지
};

export default function () {
  const res = http.get('http://3.39.31.181:8080/categories?isActive=true');

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
