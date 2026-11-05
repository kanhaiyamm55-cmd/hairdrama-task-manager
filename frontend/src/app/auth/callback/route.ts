import { NextResponse } from "next/server";

// TODO: Implement the Supabase server-side auth code exchange.
// Configure Supabase redirect URLs and use @supabase/ssr for a production cookie-based session.
export async function GET(request: Request) {
  const url = new URL(request.url);
  return NextResponse.redirect(new URL("/", url.origin));
}
