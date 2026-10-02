import { i as __toESM } from "../_runtime.mjs";
import { n as Slot, o as require_jsx_runtime, s as require_react } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { a as Printer, i as Settings2, n as SquareDashed, o as Layers, r as Settings, s as Download } from "../_libs/lucide-react.mjs";
import { i as Trigger, n as List, r as Root2, t as Content } from "../_libs/radix-ui__react-tabs.mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-CHwf1vqg.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function FusionToolbar() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "overflow-hidden rounded-xl border border-border bg-surface shadow-soft",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2 border-b border-border bg-surface-2 px-3 py-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2.5 rounded-full bg-border" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2.5 rounded-full bg-border" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2.5 rounded-full bg-border" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "ml-2 truncate font-mono text-xs text-muted",
						children: "Design · Bracket_v3"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex gap-1 overflow-x-auto px-2 py-2",
				children: [[
					"SOLID",
					"SURFACE",
					"MESH",
					"SHEET METAL"
				].map((tab) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "shrink-0 rounded-md px-2.5 py-1.5 text-xs font-medium tracking-wide text-muted",
					children: tab
				}, tab)), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "shrink-0 rounded-md bg-surface-2 px-2.5 py-1.5 text-xs font-medium tracking-wide text-fg",
					children: "MAKE"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-stretch gap-2 border-t border-border px-3 py-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "flex min-w-16 flex-1 flex-col items-center justify-center gap-1 rounded-md px-2 py-2 text-muted",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-xs tracking-wide",
							children: "3D Print"
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex min-w-28 flex-1 flex-col items-center justify-center gap-1 rounded-md bg-sage px-3 py-2 text-sage-fg",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Printer, {
							className: "size-4",
							strokeWidth: 1.75
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-center text-xs font-medium tracking-wide",
							children: "Send to Bambu"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex min-w-16 flex-1 flex-col items-center justify-center gap-1 rounded-md px-2 py-2 text-muted",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Settings, {
							className: "size-4",
							strokeWidth: 1.75
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-xs tracking-wide",
							children: "Settings"
						})]
					})
				]
			})
		]
	});
}
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var Tabs = Root2;
var TabsList = (0, import_react.forwardRef)(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, {
	ref,
	className: cn("inline-flex h-11 items-center justify-center rounded-lg bg-surface-2 p-1 text-muted", className),
	...props
}));
TabsList.displayName = "TabsList";
var TabsTrigger = (0, import_react.forwardRef)(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trigger, {
	ref,
	className: cn("inline-flex min-h-9 min-w-24 items-center justify-center rounded-md px-4 text-sm font-medium transition-colors duration-150", "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60", "data-[state=active]:bg-surface data-[state=active]:text-fg", className),
	...props
}));
TabsTrigger.displayName = "TabsTrigger";
var TabsContent = (0, import_react.forwardRef)(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Content, {
	ref,
	className: cn("mt-4 focus-visible:outline-none", className),
	...props
}));
TabsContent.displayName = "TabsContent";
var windowsSteps = [
	{
		title: "Unzip the add-in",
		body: "Download SendToBambu.zip and unzip it. You should have a folder named SendToBambu that contains SendToBambu.py and SendToBambu.manifest. Use this same folder on a Mac if you have one."
	},
	{
		title: "Add it in Fusion",
		body: "In Fusion: Utilities → Add-Ins → Scripts and Add-Ins. Open the Add-Ins tab, click the green plus next to My Add-Ins, and choose the SendToBambu folder."
	},
	{
		title: "Stop, replace, then Run",
		body: "If Send to Bambu is already loaded, click Stop. Unzip this download over the same SendToBambu folder so SendToBambu.py and stb_export.py update together. Quit Fusion, open it, select the add-in, check Run on Startup, then Run."
	},
	{
		title: "Bambu Studio path",
		body: "Auto-detect looks in Program Files, Local AppData, and the Windows App Paths registry. If yours lives elsewhere, click Locate Bambu Studio in Bambu Print Settings and pick bambu-studio.exe."
	}
];
var macSteps = [
	{
		title: "Unzip the add-in",
		body: "Download SendToBambu.zip and unzip it. Keep the SendToBambu folder intact — Fusion needs SendToBambu.py sitting next to SendToBambu.manifest. The same zip is what you install on Windows."
	},
	{
		title: "Add it in Fusion",
		body: "In Fusion: Utilities → Add-Ins → Scripts and Add-Ins. Open the Add-Ins tab, click the green plus next to My Add-Ins, and choose the SendToBambu folder."
	},
	{
		title: "Stop, replace, then Run",
		body: "If Send to Bambu is already loaded, click Stop. Unzip this download over the same SendToBambu folder so SendToBambu.py and stb_export.py update together. Quit Fusion, open it, select the add-in, check Run on Startup, then Run."
	},
	{
		title: "Bambu Studio path",
		body: "Auto-detect looks in /Applications and ~/Applications, then Spotlight. Launch uses macOS open -a so an already-running Studio gets the file. If needed, Locate Bambu Studio and pick BambuStudio.app (it behaves like a folder)."
	}
];
function StepList({ steps }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
		className: "grid gap-3",
		children: steps.map((step, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
			className: "grid grid-cols-[auto_1fr] gap-4 rounded-lg border border-border bg-surface p-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "flex size-8 items-center justify-center rounded-md bg-surface-2 font-mono text-sm text-sage",
				children: index + 1
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "min-w-0",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "text-sm font-medium text-fg",
					children: step.title
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 text-sm leading-relaxed text-muted",
					children: step.body
				})]
			})]
		}, step.title))
	});
}
function detectOs() {
	if (typeof navigator === "undefined") return "windows";
	const platform = navigator.platform || "";
	const ua = navigator.userAgent || "";
	if (/Mac|iPhone|iPad/.test(platform) || /Mac OS X/.test(ua)) return "mac";
	return "windows";
}
function InstallGuide() {
	const [os, setOs] = (0, import_react.useState)("windows");
	(0, import_react.useEffect)(() => {
		setOs(detectOs());
	}, []);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Tabs, {
		defaultValue: os,
		className: "w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TabsList, {
				className: "w-full sm:w-auto",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger, {
					value: "windows",
					className: "flex-1 sm:flex-none",
					children: "Windows"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger, {
					value: "mac",
					className: "flex-1 sm:flex-none",
					children: "Mac"
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
				value: "windows",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StepList, { steps: windowsSteps })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
				value: "mac",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StepList, { steps: macSteps })
			})
		]
	}, os);
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-[opacity,transform,background-color,color] duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-40 active:scale-[0.98] [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0", {
	variants: {
		variant: {
			default: "bg-accent text-accent-fg hover:opacity-90",
			sage: "bg-sage text-sage-fg hover:opacity-90",
			outline: "border border-border bg-transparent text-fg hover:bg-surface-2",
			ghost: "text-fg hover:bg-surface-2"
		},
		size: {
			default: "h-11 px-4",
			sm: "h-9 px-3 text-xs",
			lg: "h-12 px-5 text-base"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
function Button({ className, variant, size, asChild = false, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		className: cn(buttonVariants({
			variant,
			size
		}), className),
		...props
	});
}
var DOWNLOAD_HREF = "/downloads/SendToBambu.zip";
function DownloadButton({ size = "lg", variant = "default" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
		variant,
		size,
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("a", {
			href: DOWNLOAD_HREF,
			download: "SendToBambu.zip",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, {}), "Download add-in"]
		})
	});
}
function Home() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-bg text-fg",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
			className: "sticky top-0 z-20 border-b border-border/80 bg-bg/90 backdrop-blur-sm",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto flex h-14 max-w-5xl items-center justify-between px-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("a", {
					href: "#top",
					className: "flex items-center gap-2 text-sm font-medium",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Printer, {
						className: "size-4 text-sage",
						strokeWidth: 1.75
					}), "Send to Bambu"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, { size: "default" })]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			id: "top",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "mx-auto grid max-w-5xl gap-10 px-4 py-12 sm:py-16 lg:grid-cols-[1.15fr_0.85fr] lg:items-center lg:py-20",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-mono text-xs tracking-wide text-sage",
							children: "Fusion add-in · Windows & Mac"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
							className: "mt-3 max-w-xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl",
							children: "One button. Every visible body. Bambu Studio."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-4 max-w-lg text-base leading-relaxed text-muted",
							children: "Drop a Print button into Fusion. It takes every visible solid — no selecting — writes a millimeter 3MF, and opens Bambu Studio. One zip installs on a Windows PC and a Mac."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 max-w-lg text-sm leading-relaxed text-sage",
							children: "1.3.1: every visible solid, and the mesh is written in millimeters — Fusion is told to export mm instead of scaling centimeters. Stop the old add-in, replace the folder, quit Fusion, then Run."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-7 flex flex-wrap items-center gap-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "lg",
								asChild: true,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
									href: "#install",
									children: "Install steps"
								})
							})]
						})
					] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(FusionToolbar, {})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
					className: "border-y border-border bg-surface",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mx-auto grid max-w-5xl gap-8 px-4 py-12 sm:grid-cols-3",
						children: [
							{
								icon: SquareDashed,
								title: "Every visible solid",
								body: "No selection. It takes every visible solid in the design, including assembly instances. Hide a body in the browser to leave it off the plate."
							},
							{
								icon: Layers,
								title: "Exports in mm",
								body: "Writes 3MF in millimeters so the part does not come in 10× small. STL is optional in settings."
							},
							{
								icon: Printer,
								title: "Opens Bambu Studio",
								body: "Windows launches bambu-studio.exe. Mac uses open -a on BambuStudio.app so a Studio window that is already open gets the file."
							}
						].map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "min-w-0",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(item.icon, {
									className: "size-5 text-sage",
									strokeWidth: 1.75
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
									className: "mt-3 text-base font-medium",
									children: item.title
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "mt-2 text-sm leading-relaxed text-muted",
									children: item.body
								})
							]
						}, item.title))
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					id: "install",
					className: "mx-auto max-w-5xl px-4 py-14",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-mono text-xs tracking-wide text-sage",
							children: "Install"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "mt-2 text-2xl font-semibold tracking-tight",
							children: "Same add-in on both machines"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 max-w-2xl text-sm leading-relaxed text-muted",
							children: "Fusion loads this as a Python add-in. The button is identical on Windows and Mac; only the Bambu Studio path changes, and that is auto-detected."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-8",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(InstallGuide, {})
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
					className: "border-y border-border bg-surface",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mx-auto grid max-w-5xl gap-10 px-4 py-14 lg:grid-cols-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-mono text-xs tracking-wide text-sage",
								children: "What it sends"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
								className: "mt-2 text-2xl font-semibold tracking-tight",
								children: "All visible solids, nothing to pick"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
								className: "mt-5 grid gap-3 text-sm leading-relaxed text-muted",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
										className: "rounded-lg border border-border bg-bg px-4 py-3",
										children: "Every visible solid in the root component."
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
										className: "rounded-lg border border-border bg-bg px-4 py-3",
										children: "Visible bodies in assembly occurrences, in world position."
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
										className: "rounded-lg border border-border bg-bg px-4 py-3",
										children: "Hidden bodies (browser light bulb off) are skipped."
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
										className: "rounded-lg border border-border bg-bg px-4 py-3",
										children: "Several bodies — one 3MF with a named object per body."
									})
								]
							})
						] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-mono text-xs tracking-wide text-sage",
								children: "Settings"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", {
								className: "mt-2 flex items-center gap-2 text-2xl font-semibold tracking-tight",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Settings2, {
									className: "size-6 text-sage",
									strokeWidth: 1.75
								}), "Bambu Print Settings"]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-3 text-sm leading-relaxed text-muted",
								children: "Mesh quality, 3MF vs STL, whether to launch Studio, and an optional path if auto-detect misses your install."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
								className: "mt-5 grid gap-3 font-mono text-xs text-muted",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "rounded-lg border border-border bg-bg px-4 py-3",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
										className: "text-subtle",
										children: "Windows"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
										className: "mt-1 break-all text-fg",
										children: "C:\\Program Files\\Bambu Studio\\bambu-studio.exe"
									})]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "rounded-lg border border-border bg-bg px-4 py-3",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
										className: "text-subtle",
										children: "Mac"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
										className: "mt-1 break-all text-fg",
										children: "/Applications/BambuStudio.app"
									})]
								})]
							})
						] })]
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "mx-auto max-w-5xl px-4 py-14",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-2xl font-semibold tracking-tight",
							children: "If something misses"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-6 grid gap-3 sm:grid-cols-2",
							children: [
								{
									q: "No visible solid body found",
									a: "Turn on the bodies you want in the browser (light bulb on). Hidden and surface bodies are skipped. You do not need to select anything."
								},
								{
									q: "Bambu Studio was not found",
									a: "Install Studio, then either relaunch Fusion or paste the .exe / .app path in Bambu Print Settings."
								},
								{
									q: "Part is the wrong size in Bambu",
									a: "That was the old ×10 centimeter scale on a file Fusion already wrote in mm. Download 1.3.1, Stop Send to Bambu, replace the whole folder, quit Fusion, then Run."
								},
								{
									q: "Button is missing",
									a: "Scripts and Add-Ins → Add-Ins → Send to Bambu → Run. Enable Run on Startup so it survives a Fusion restart."
								},
								{
									q: "scale_binary_stl error",
									a: "Fusion kept the previous helper in memory. Download this zip, Stop Send to Bambu, unzip over the whole folder (SendToBambu.py and stb_export.py together), quit Fusion, open it, then Run."
								}
							].map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "rounded-lg border border-border bg-surface p-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
									className: "text-sm font-medium",
									children: item.q
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "mt-2 text-sm leading-relaxed text-muted",
									children: item.a
								})]
							}, item.q))
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-10 flex flex-wrap items-center gap-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DownloadButton, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm text-muted",
								children: "Zip includes the add-in and a short README."
							})]
						})
					]
				})
			]
		})]
	});
}
//#endregion
export { Home as component };
