// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

interface MessagePayload {
  record: {
    id: string;
    conversation_id: string;
    role: string;
    content: string;
    created_at: string;
  };
  type: "INSERT";
  table: "messages";
  schema: "public";
  old_record: null;
}

console.info('Supabase Edge Function: call-gcf started');

Deno.serve(async (req: Request) => {
  try {
    const payload: MessagePayload = await req.json();
    const newMessage = payload.record;

    // Ensure it's an assistant message
    if (newMessage.role !== 'assistant') {
      console.log('Not an assistant message, skipping GCF call.');
      return new Response(JSON.stringify({ message: 'Not an assistant message' }), {
        headers: { 'Content-Type': 'application/json' },
        status: 200,
      });
    }

    console.log(`Calling GCF for conversation_id: ${newMessage.conversation_id}`);

    // Replace with your actual Google Cloud Function URL
    const googleCloudFunctionUrl = Deno.env.get('GOOGLE_CLOUD_FUNCTION_URL');

    if (!googleCloudFunctionUrl) {
      console.error('GOOGLE_CLOUD_FUNCTION_URL environment variable not set.');
      return new Response(JSON.stringify({ error: 'Server configuration error' }), {
        headers: { 'Content-Type': 'application/json' },
        status: 500,
      });
    }

    const gcfResponse = await fetch(googleCloudFunctionUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: newMessage.content,
        conversation_id: newMessage.conversation_id,
      }),
    });

    if (!gcfResponse.ok) {
      const errorText = await gcfResponse.text();
      console.error(`GCF call failed: ${gcfResponse.status} - ${errorText}`);
      return new Response(JSON.stringify({ error: `GCF call failed: ${errorText}` }), {
        headers: { 'Content-Type': 'application/json' },
        status: gcfResponse.status,
      });
    }

    const gcfResult = await gcfResponse.text(); // Or .json() if your GCF returns JSON
    console.log('GCF call successful:', gcfResult);

    return new Response(
      JSON.stringify({ message: 'GCF called successfully', gcfResult }),
      { headers: { 'Content-Type': 'application/json', 'Connection': 'keep-alive' }}
    );
  } catch (error) {
    console.error('Error in Edge Function:', error.message);
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { 'Content-Type': 'application/json' },
      status: 500,
    });
  }
});
