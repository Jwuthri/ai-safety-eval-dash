"use client";

import { ChatContainer } from "@/components/chat/chat-container";

export const dynamic = 'force-dynamic';

export default function ChatPage() {
  // Note: Clerk authentication temporarily disabled for deployment
  // const { isLoaded, userId } = useAuth();
  // useEffect(() => {
  //   if (isLoaded && !userId) {
  //     redirect("/");
  //   }
  // }, [isLoaded, userId]);

  return (
    <div className="h-screen bg-gradient-to-br from-gray-950 via-blue-950 to-purple-950">
      <ChatContainer />
    </div>
  );
}
