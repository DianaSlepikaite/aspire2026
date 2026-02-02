import { TalentMatchMark } from "@/components/brand/TalentMatchMark";

interface SidebarHeaderProps {
  isBusiness: boolean;
}

export function SidebarHeader({ isBusiness }: SidebarHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-12">
      <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
        <TalentMatchMark className="size-5 text-primary-foreground" />
      </div>
      <h2 className="text-foreground text-xl font-bold tracking-tight">TalentMatch</h2>
      <span className="bg-success/10 text-success text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
        {isBusiness ? "Business" : "Career"}
      </span>
    </div>
  );
}
