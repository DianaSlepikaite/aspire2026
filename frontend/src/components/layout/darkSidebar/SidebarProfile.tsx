import { Button } from "@/components/ui/button";

interface SidebarProfileProps {
  userName: string;
  userRole: string;
  userImage: string;
  onExit: () => void;
}

export function SidebarProfile({ userName, userRole, userImage, onExit }: SidebarProfileProps) {
  return (
    <div className="mt-auto pt-8 flex items-center gap-4 border-t border-border">
      <div
        className="size-10 rounded-full bg-cover bg-center border border-border"
        style={{ backgroundImage: `url('${userImage}')` }}
        role="img"
        aria-label={`${userName} avatar`}
      />
      <div className="flex-1 min-w-0">
        <p className="text-foreground text-sm font-semibold truncate">{userName}</p>
        <p className="text-muted-foreground text-xs truncate">{userRole}</p>
      </div>
      <Button
        onClick={onExit}
        variant="ghost"
        size="icon"
        className="text-muted-foreground hover:text-foreground"
        aria-label="Return to portal selection"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="size-5"
        >
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" x2="9" y1="12" y2="12" />
        </svg>
      </Button>
    </div>
  );
}
