const CREATE_ARCHIVE_LINK_EVENT = "createArchiveLink";
const createArchiveLinkEvent = new Event(CREATE_ARCHIVE_LINK_EVENT);

class DownloadArchive {
  constructor(el) {
    this.el = el;

    this.collectionPath = el.getAttribute("data-download");
    this.collectionName = el.getAttribute("data-collection");

    this.loadingState = this.createState(false, this.el);
    this.init();
  }

  init() {
    this.el.addEventListener("click", this.handleClick.bind(this));
    this.el.addEventListener(
      CREATE_ARCHIVE_LINK_EVENT,
      this.handleCreateArchiveLink.bind(this)
    );
  }

  get endpoint() {
    return `/api/collections/${this.collectionPath}/zip`;
  }

  async createArchiveLink() {
    const [, setIsLoading] = this.loadingState;

    setIsLoading(true);

    try {
      const response = await fetch(this.endpoint).then((res) => res.json());
      this.link = response.data;
    } catch (e_) {
      throw new Error();
    } finally {
      setIsLoading(false);
    }
  }

  createState(value, el) {
    let v = value;

    function getValue() {
      return v;
    }

    function setValue(newValue) {
      if (typeof newValue === "function") {
        v = newValue(v);
      } else {
        v = newValue;
      }

      el.dispatchEvent(createArchiveLinkEvent);
    }

    return [getValue, setValue];
  }

  handleClick(e) {
    e.preventDefault();

    this.createArchiveLink().catch(() => {
      this.el.setAttribute("disabled", true);
      this.el.innerText = "Download fehlgeschlagen.";
    });
  }

  handleCreateArchiveLink() {
    const [getValue] = this.loadingState;

    const isLoading = getValue();

    if (isLoading) {
      this.el.setAttribute("disabled", true);
      this.el.innerText = "Erstelle Link...";
    } else {
      this.el.removeAttribute("disabled");
      this.el.innerText = "Downloadlink erstellen";
    }

    if (this.link) {
      const nav = document.querySelector("nav");

      this.el.removeEventListener("click", this.handleClick.bind(this));
      this.el.removeEventListener(
        CREATE_ARCHIVE_LINK_EVENT,
        this.handleCreateArchiveLink.bind(this)
      );
      const a = document.createElement("a");
      a.href = this.link;
      a.classList.add("button");
      a.download = this.collectionName + ".zip";
      a.innerText = "Herunterladen";

      nav.append(a);
      this.el.remove();
    }
  }
}

window.onload = function onLoad() {
  const button = document.querySelector("[data-download]");

  new DownloadArchive(button);
};
