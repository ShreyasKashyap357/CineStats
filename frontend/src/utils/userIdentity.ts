const USER_ID_KEY = 'cine_stats_user_id';

export function getUserIdentity(): string {
  let userId = localStorage.getItem(USER_ID_KEY);
  
  if (!userId) {
    // Use built-in crypto.randomUUID for modern browsers
    userId = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, userId);
  }
  
  return userId;
}

export function resetUserIdentity(): void {
  localStorage.removeItem(USER_ID_KEY);
}
