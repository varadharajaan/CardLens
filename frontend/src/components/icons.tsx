import type { SVGProps } from "react";

type P = SVGProps<SVGSVGElement>;
const base = { width: 20, height: 20, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round" } as const;

export const IGrid = (p: P) => (<svg {...base} {...p}><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/></svg>);
export const ICard = (p: P) => (<svg {...base} {...p}><rect x="2" y="5" width="20" height="14" rx="3"/><path d="M2 10h20"/></svg>);
export const IBank = (p: P) => (<svg {...base} {...p}><path d="M3 10l9-6 9 6"/><path d="M5 10v9M19 10v9M9 10v9M15 10v9M3 21h18"/></svg>);
export const IDoc = (p: P) => (<svg {...base} {...p}><path d="M14 3v5h5"/><path d="M5 3h9l5 5v13H5z"/><path d="M9 13h6M9 17h6"/></svg>);
export const IUpload = (p: P) => (<svg {...base} {...p}><path d="M12 16V4M7 9l5-5 5 5"/><path d="M5 20h14"/></svg>);
export const IRupee = (p: P) => (<svg {...base} {...p}><path d="M7 4h10M7 8h10M9 8c4 0 4 7-2 7l6 5"/></svg>);
export const IGift = (p: P) => (<svg {...base} {...p}><rect x="3" y="8" width="18" height="13" rx="2"/><path d="M3 12h18M12 8v13"/><path d="M12 8S9 3 6.5 5 9 8 12 8zM12 8s3-5 5.5-3-1.5 3-5.5 3z"/></svg>);
export const ITrophy = (p: P) => (<svg {...base} {...p}><path d="M8 4h8v4a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 3M16 6h3a3 3 0 0 1-3 3M10 14h4l-1 4h-2z"/></svg>);
export const IAlert = (p: P) => (<svg {...base} {...p}><path d="M12 9v4M12 17h.01M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>);
export const ISignout = (p: P) => (<svg {...base} {...p}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>);
export const ITrend = (p: P) => (<svg {...base} {...p}><path d="M3 17l6-6 4 4 7-7M14 8h7v7"/></svg>);
export const ISpark = (p: P) => (<svg {...base} {...p}><path d="M13 2 9.5 9.5 2 13l7.5 3.5L13 24l3.5-7.5L24 13l-7.5-3.5z" transform="scale(.88) translate(1.6 0)"/></svg>);
export const ITarget = (p: P) => (<svg {...base} {...p}><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>);
export const IWallet = (p: P) => (<svg {...base} {...p}><path d="M4 7h16v12H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h13"/><path d="M16 12h4v4h-4a2 2 0 0 1 0-4z"/></svg>);
export const IMail = (p: P) => (<svg {...base} {...p}><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 7 9 7 9-7"/></svg>);
export const IFolder = (p: P) => (<svg {...base} {...p}><path d="M3 6h6l2 2h10v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>);
export const IShield = (p: P) => (<svg {...base} {...p}><path d="M12 3 20 7v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z"/><path d="m9 12 2 2 4-5"/></svg>);
export const IRepeat = (p: P) => (<svg {...base} {...p}><path d="M17 2l4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/></svg>);
export const IInbox = (p: P) => (<svg {...base} {...p}><path d="M4 4h16l2 10v5a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-5z"/><path d="M2 14h6a4 4 0 0 0 8 0h6"/></svg>);
