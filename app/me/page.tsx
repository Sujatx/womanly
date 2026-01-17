import { createServerSupabase } from "@/lib/supabase/server";

export default async function Me() {
  const supabase = await createServerSupabase();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return <pre>null</pre>;
  }

  // Load profile row
  const { data: profile } = await supabase
    .from("profiles")
    .select("*")
    .eq("id", user.id)
    .single();

  return (
    <pre>{JSON.stringify({ user, profile }, null, 2)}</pre>
  );
}
