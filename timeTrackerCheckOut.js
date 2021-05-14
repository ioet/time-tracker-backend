import { check } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";
export let errorRate = new Rate("errors");

export let options = {
  thresholds: {
    errors: ["rate<0.1"], // <10% errors
  },
};

export default function () {
  const url = http.get("https://timetracker-api.azurewebsites.net");
  let passed = check(url, {
    "status is 200": (r) => r.status === 200,
  });
  if (!passed) {
    errorRate.add(1);
  }
}

export function handleSummary(data) {
  console.log("Preparing the end-of-test summary...");
  return {
    stdout: textSummary(data, { indent: " ", enableColors: true }),
    "summary.json": JSON.stringify(data),
  };
}
