// Dynamic Role-Aware Navbar Module

document.addEventListener('DOMContentLoaded', () => {
    renderNavbar();
});

function renderNavbar() {
    const navContainer = document.getElementById('main-nav');
    if (!navContainer) return;

    const authenticated = isAuthenticated();
    const user = getCurrentUser();

    // Base path for the frontend
    const FRONTEND = '/frontend';

    let roleDashboardLink = '';

    if (authenticated && user) {
        const role = user.role;

        let dashboardPath = `${FRONTEND}/pages/${role}/dashboard.html`;

        roleDashboardLink = `
            <a href="${dashboardPath}"
               class="text-sm font-semibold text-primary-blue hover:text-navy-dark">
                Dashboard (${role.toUpperCase()})
            </a>
        `;
    }

    const navHtml = `
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-20">

                <!-- Logo -->
                <a href="${FRONTEND}/index.html"
                   class="flex items-center gap-2">

                    <div class="w-10 h-10 rounded-xl bg-red-600
                                flex items-center justify-center
                                text-white font-extrabold text-xl shadow-lg">
                        ✚
                    </div>

                    <div>
                        <span class="text-2xl font-extrabold tracking-tight text-slate-900">
                            Life<span class="text-red-600">Link</span>
                        </span>

                        <span class="block text-xs font-semibold text-slate-500
                                     uppercase tracking-widest">
                            Emergency Healthcare
                        </span>
                    </div>

                </a>

                <!-- Desktop Menu -->
                <div class="hidden md:flex items-center space-x-8">

                    <a href="${FRONTEND}/index.html"
                       class="text-slate-700 hover:text-red-600 font-medium transition">
                        Home
                    </a>

                    <a href="${FRONTEND}/pages/about.html"
                       class="text-slate-700 hover:text-red-600 font-medium transition">
                        About
                    </a>

                    <a href="${FRONTEND}/pages/find-blood.html"
                       class="text-slate-700 hover:text-red-600 font-medium transition">
                        Find Blood
                    </a>

                    <a href="${FRONTEND}/pages/medicine-locator.html"
                       class="text-slate-700 hover:text-red-600 font-medium transition">
                        Medicine Locator
                    </a>

                    ${roleDashboardLink}

                </div>

                <!-- Right Auth Actions -->
                <div class="flex items-center gap-4">

                    <a href="${FRONTEND}/pages/emergency-request.html"
                       class="btn-emergency text-sm">
                        <span>🚨</span> Emergency Request
                    </a>

                    ${authenticated ? `

                        <a href="${FRONTEND}/pages/notifications.html"
                           class="relative p-2 text-slate-600 hover:text-red-600">

                            <span class="text-xl">🔔</span>

                            <span id="unread-badge"
                                  class="hidden absolute top-0 right-0 w-4 h-4
                                         bg-red-600 text-white text-xs rounded-full
                                         flex items-center justify-center font-bold">
                            </span>

                        </a>

                        <button onclick="logoutUser()"
                                class="btn-outline text-sm">
                            Logout
                        </button>

                    ` : `

                        <a href="${FRONTEND}/pages/login.html"
                           class="text-slate-700 font-semibold hover:text-red-600">
                            Login
                        </a>

                        <a href="${FRONTEND}/pages/register.html"
                           class="btn-blue text-sm">
                            Register
                        </a>

                    `}

                </div>

            </div>
        </div>
    `;

    navContainer.innerHTML = navHtml;
}