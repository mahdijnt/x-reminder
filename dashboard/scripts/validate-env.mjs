const required = ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_APP_URL"];
const missing = required.filter((key) => !process.env[key]);
if (missing.length) { console.error("Missing required dashboard environment variables:"); for (const key of missing) console.error(`- ${key}`); process.exit(1); }
console.log("Dashboard environment validation passed.");
