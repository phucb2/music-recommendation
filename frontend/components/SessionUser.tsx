/** Who is signed in — keep next to Logout. */
export function SessionUser({ username }: { username: string }) {
  return (
    <p className="max-w-full text-right text-sm text-muted">
      <span className="text-muted/90">Signed in as </span>
      <span
        className="inline-block max-w-[10rem] truncate align-bottom font-semibold text-foreground sm:max-w-xs"
        title={username}
      >
        {username}
      </span>
    </p>
  );
}
