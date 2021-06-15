import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { Rate } from 'k6/metrics';
import { randomIntBetween} from "https://jslib.k6.io/k6-utils/1.0.0/index.js";

export let errorRate = new Rate("errors");


export const options = {
  stages: [
    { duration: "15s", target: 5 },
    { duration: "150s", target: 5 },
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    error_rate: ["rate < 0.1"],
    http_req_duration: ["p(95)<2000"],
  }
};

export function setup() {
  let authToken = `${__ENV.ID_TOKEN}`;
  console.log(authToken);
  return authToken;
}

export default (authToken) => {
    let response;
    let params = {
      headers: {
        "Accept": "application/json, text/plain, */*",
        "Authorization": `Bearer ${authToken}`
            }
    };

    group("home page", function () {

      check (http.get(`${url}/users/${userId}`,params),{
        "status is 200": (r) => r.status === 200
      });

      check (http.get(`${url}/time-entries/running`,params),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      });

      check (http.get(`${url}/time-entries/summary?time_offset=300`,params),{
        "status is 200": (r) => r.status === 200
      });

      check (http.get(`${url}//projects`,params),{
        "status is 200": (r) => r.status === 200
      });

      check (http.get(`${url}/time-entries/running`,params),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      });

      /* check ( http.options("https://time-tracker-config.azconfig.io/kv?key=.appconfig.featureflag%2F*&api-version=1.0"
      ),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      }); */

      sleep(randomIntBetween(3, 10));
        
      check (http.get(`${url}/users/${userId}`,params),{
          "status is 200": (r) => r.status === 200
        });
  
      check (http.get(`${url}/time-entries/running`,params),{
          "status is 200": (r) => r.status === 200 || r.status === 204
        });
  
      check (http.get(`${url}/time-entries/summary?time_offset=300`,params),{
          "status is 200": (r) => r.status === 200
        });

      /* check ( http.get("https://time-tracker-config.azconfig.io/kv?key=.appconfig.featureflag%2F*&api"
      ),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      });
 */
      check (http.get(`${url}//projects`,params),{
        "status is 200": (r) => r.status === 200
      });

      check (http.get(`${url}/time-entries/running`,params),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      });

      check (http.get(`${url}/time-entries/running`,params),{
        "status is 200": (r) => r.status === 200 || r.status === 204
      });
    });
  
}