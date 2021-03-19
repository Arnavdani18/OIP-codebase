frappe.ready(async () => {
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = m => new Promise(r => setTimeout(r, m));
  await sleep(200);
});
